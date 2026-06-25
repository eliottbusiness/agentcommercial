-- ============================================
-- SCHEMA SUPABASE - CRM PROSPECTION COMMERCIALE
-- Version: 1.0 | Stack: 100% gratuite (Free Tier: 500MB, 50K MAU)
-- ============================================

-- Activer l'extension UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- TABLE PRINCIPALE: PROSPECTS
-- ============================================
CREATE TABLE IF NOT EXISTS prospects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identifiants officiels (SIRENE)
    siren VARCHAR(9) UNIQUE,
    siret VARCHAR(14) UNIQUE,

    -- Identité entreprise
    company_name VARCHAR(255) NOT NULL,
    legal_form VARCHAR(100),
    brand_name VARCHAR(255),

    -- Classification sectorielle
    naf_code VARCHAR(10),
    naf_label VARCHAR(255),
    sector_category VARCHAR(100),

    -- Localisation
    address TEXT,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    department_code VARCHAR(3),
    region VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Taille / Maturité
    employee_count_band VARCHAR(20),
    employee_count_exact INTEGER,
    revenue_estimate DECIMAL(15, 2),
    revenue_exact DECIMAL(15, 2),
    creation_date DATE,

    -- Contact & Digital
    website VARCHAR(500),
    linkedin_url VARCHAR(500),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),

    -- Décideur identifié
    decision_maker_name VARCHAR(255),
    decision_maker_title VARCHAR(100),
    decision_maker_linkedin VARCHAR(500),
    decision_maker_email VARCHAR(255),

    -- Scoring & Intention (CLÉ POUR 1 PROSPECT = 1 CLIENT)
    intent_score INTEGER CHECK (intent_score >= 0 AND intent_score <= 100),
    intent_signals JSONB DEFAULT '{}',
    fit_score INTEGER CHECK (fit_score >= 0 AND fit_score <= 100),
    priority_score INTEGER GENERATED ALWAYS AS (
        (COALESCE(intent_score, 0) * 0.6 + COALESCE(fit_score, 0) * 0.4)::INTEGER
    ) STORED,

    -- Status pipeline
    status VARCHAR(50) DEFAULT 'discovered' CHECK (
        status IN ('discovered', 'enriched', 'qualified', 'hot_lead', 
                   'contacted', 'responded', 'meeting_booked', 'proposal_sent',
                   'negotiation', 'won', 'lost', 'nurture')
    ),

    -- Source & Traçabilité
    source VARCHAR(100),
    discovery_method VARCHAR(100),

    -- Métadonnées temporelles
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_enrichment_date TIMESTAMP WITH TIME ZONE,
    last_contact_date TIMESTAMP WITH TIME ZONE,
    next_action_date TIMESTAMP WITH TIME ZONE,

    -- Flags qualité
    is_verified BOOLEAN DEFAULT FALSE,
    is_duplicated BOOLEAN DEFAULT FALSE,
    duplicate_of UUID REFERENCES prospects(id),

    -- Notes & Contexte
    notes TEXT,
    tags TEXT[] DEFAULT '{}',

    -- Row Level Security (RLS) - obligatoire Supabase
    user_id UUID REFERENCES auth.users(id)
);

-- Index pour performances
CREATE INDEX idx_prospects_status ON prospects(status);
CREATE INDEX idx_prospects_priority_score ON prospects(priority_score DESC);
CREATE INDEX idx_prospects_intent_score ON prospects(intent_score DESC);
CREATE INDEX idx_prospects_city ON prospects(city);
CREATE INDEX idx_prospects_naf ON prospects(naf_code);
CREATE INDEX idx_prospects_source ON prospects(source);
CREATE INDEX idx_prospects_created_at ON prospects(created_at);
CREATE INDEX idx_prospects_next_action ON prospects(next_action_date) WHERE next_action_date IS NOT NULL;
CREATE INDEX idx_prospects_tags ON prospects USING GIN(tags);
CREATE INDEX idx_prospects_intent_signals ON prospects USING GIN(intent_signals);

-- ============================================
-- TABLE INTERACTIONS (Suivi touches)
-- ============================================
CREATE TABLE IF NOT EXISTS interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL CHECK (
        interaction_type IN ('email_sent', 'email_opened', 'email_replied', 
                            'email_bounced', 'call_made', 'call_connected',
                            'meeting_booked', 'meeting_completed', 'meeting_no_show',
                            'linkedin_view', 'linkedin_connect', 'linkedin_message',
                            'twitter_mention', 'reddit_mention', 'website_visit',
                            'proposal_sent', 'proposal_viewed', 'proposal_signed',
                            'note', 'task_created', 'status_change')
    ),
    channel VARCHAR(50) CHECK (
        channel IN ('email', 'linkedin', 'phone', 'cal_com', 'twitter', 
                   'reddit', 'website', 'direct', 'referral', 'other')
    ),
    content TEXT,
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative', 'mixed')),
    opened_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,
    click_count INTEGER DEFAULT 0,
    cal_com_event_id VARCHAR(255),
    email_message_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_interactions_prospect ON interactions(prospect_id);
CREATE INDEX idx_interactions_type ON interactions(interaction_type);
CREATE INDEX idx_interactions_created ON interactions(created_at);

-- ============================================
-- TABLE SEQUENCES (Séquences d'outreach)
-- ============================================
CREATE TABLE IF NOT EXISTS outreach_sequences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID NOT NULL REFERENCES prospects(id) ON DELETE CASCADE,
    sequence_name VARCHAR(100) NOT NULL,
    step_number INTEGER NOT NULL,
    step_type VARCHAR(50) CHECK (
        step_type IN ('email', 'linkedin_message', 'phone_call', 
                     'twitter_mention', 'content_share', 'wait', 'trigger')
    ),
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN ('pending', 'sent', 'delivered', 'opened', 'replied', 
                  'bounced', 'failed', 'skipped', 'completed')
    ),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    content_template TEXT,
    personalized_content TEXT,
    personalization_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_sequences_prospect ON outreach_sequences(prospect_id);
CREATE INDEX idx_sequences_status ON outreach_sequences(status);
CREATE INDEX idx_sequences_scheduled ON outreach_sequences(scheduled_at) WHERE status = 'pending';

-- ============================================
-- TABLE SIGNALS (Signaux d'intention bruts)
-- ============================================
CREATE TABLE IF NOT EXISTS intent_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prospect_id UUID REFERENCES prospects(id) ON DELETE CASCADE,
    signal_type VARCHAR(100) NOT NULL,
    signal_source VARCHAR(100) NOT NULL,
    signal_data JSONB NOT NULL,
    confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    impact_score INTEGER CHECK (impact_score >= 1 AND impact_score <= 10),
    is_processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_signals_prospect ON intent_signals(prospect_id);
CREATE INDEX idx_signals_type ON intent_signals(signal_type);
CREATE INDEX idx_signals_unprocessed ON intent_signals(is_processed) WHERE is_processed = FALSE;
CREATE INDEX idx_signals_confidence ON intent_signals(confidence_score DESC);

-- ============================================
-- TABLE ICP (Ideal Customer Profile)
-- ============================================
CREATE TABLE IF NOT EXISTS icp_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    criterion_name VARCHAR(100) NOT NULL,
    criterion_type VARCHAR(50) CHECK (
        criterion_type IN ('sector', 'size', 'location', 'tech_stack', 
                          'revenue_range', 'growth_stage', 'pain_point', 'behavior')
    ),
    weight DECIMAL(3, 2) NOT NULL CHECK (weight >= 0 AND weight <= 1),
    match_rules JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- VUES ANALYTIQUES
-- ============================================

CREATE OR REPLACE VIEW hot_prospects_today AS
SELECT 
    p.*,
    COUNT(i.id) FILTER (WHERE i.created_at > NOW() - INTERVAL '30 days') as interactions_30d,
    MAX(i.created_at) as last_interaction_date
FROM prospects p
LEFT JOIN interactions i ON p.id = i.prospect_id
WHERE 
    p.status IN ('hot_lead', 'qualified')
    AND (p.next_action_date IS NULL OR p.next_action_date <= NOW())
    AND p.is_duplicated = FALSE
GROUP BY p.id
ORDER BY p.priority_score DESC, p.intent_score DESC
LIMIT 50;

CREATE OR REPLACE VIEW conversion_funnel AS
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*)::numeric / NULLIF(SUM(COUNT(*)) OVER (), 0) * 100, 2) as percentage
FROM prospects
WHERE created_at > NOW() - INTERVAL '90 days'
GROUP BY status
ORDER BY 
    CASE status
        WHEN 'discovered' THEN 1
        WHEN 'enriched' THEN 2
        WHEN 'qualified' THEN 3
        WHEN 'hot_lead' THEN 4
        WHEN 'contacted' THEN 5
        WHEN 'responded' THEN 6
        WHEN 'meeting_booked' THEN 7
        WHEN 'proposal_sent' THEN 8
        WHEN 'negotiation' THEN 9
        WHEN 'won' THEN 10
        WHEN 'lost' THEN 11
        ELSE 12
    END;

CREATE OR REPLACE VIEW source_performance AS
SELECT 
    source,
    COUNT(*) as total_prospects,
    COUNT(*) FILTER (WHERE status = 'won') as won_count,
    COUNT(*) FILTER (WHERE status = 'meeting_booked') as meetings_count,
    ROUND(AVG(intent_score), 2) as avg_intent_score,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'won')::numeric / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as win_rate,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'meeting_booked')::numeric / 
        NULLIF(COUNT(*), 0) * 100, 2
    ) as meeting_rate
FROM prospects
WHERE created_at > NOW() - INTERVAL '90 days'
GROUP BY source
ORDER BY win_rate DESC NULLS LAST;

-- ============================================
-- FONCTIONS & TRIGGERS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_prospects_updated_at 
    BEFORE UPDATE ON prospects 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION log_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO interactions (prospect_id, interaction_type, content, channel, created_at)
        VALUES (
            NEW.id, 
            'status_change', 
            jsonb_build_object('from', OLD.status, 'to', NEW.status)::text,
            'direct',
            NOW()
        );
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER log_prospect_status_change
    AFTER UPDATE OF status ON prospects
    FOR EACH ROW
    EXECUTE FUNCTION log_status_change();

-- ============================================
-- ROW LEVEL SECURITY (RLS) - Supabase
-- ============================================

ALTER TABLE prospects ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE intent_signals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own prospects"
    ON prospects FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own interactions"
    ON interactions FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own sequences"
    ON outreach_sequences FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY "Users can only access their own signals"
    ON intent_signals FOR ALL
    USING (auth.uid() = user_id);

-- ============================================
-- DONNÉES INITIALES: ICP Template
-- ============================================

INSERT INTO icp_criteria (criterion_name, criterion_type, weight, match_rules) VALUES
('Secteur Tech & Digital', 'sector', 0.25, '{"naf_codes": ["62.01Z", "62.02A", "62.03Z", "63.11Z", "63.12Z", "58.29Z", "61.10Z"]}'),
('Taille PME (10-250 salariés)', 'size', 0.20, '{"min_employees": 10, "max_employees": 250}'),
('Croissance / Startup', 'growth_stage', 0.15, '{"indicators": ["recent_funding", "hiring_spree", "new_office"]}'),
('Stack Technique Moderne', 'tech_stack', 0.15, '{"technologies": ["React", "Node.js", "Python", "AWS", "Docker", "Kubernetes"]}'),
('Besoin Identifié', 'pain_point', 0.25, '{"pain_points": ["scaling", "digital_transformation", "automation", "data_pipeline"]}');

-- ============================================
-- COMMENTAIRES DOCUMENTAIRES
-- ============================================

COMMENT ON TABLE prospects IS 'Table principale des prospects commerciaux avec scoring intention';
COMMENT ON COLUMN prospects.intent_score IS 'Score 0-100: probabilité d achat basée sur signaux comportementaux';
COMMENT ON COLUMN prospects.fit_score IS 'Score 0-100: alignement avec ICP (Ideal Customer Profile)';
COMMENT ON COLUMN prospects.priority_score IS 'Score composite: 60% intent + 40% fit';
COMMENT ON COLUMN prospects.intent_signals IS 'JSON des signaux d intention détectés (job postings, funding, etc.)';
COMMENT ON TABLE intent_signals IS 'Signaux d intention bruts collectés avant traitement';
COMMENT ON TABLE interactions IS 'Historique de toutes les interactions avec les prospects';
