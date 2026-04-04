-- -----------------------------------------------------------------------------
-- MHWs Equipment Manager - Supabase Setup Script
-- -----------------------------------------------------------------------------

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. weapons (EquipmentBox)
CREATE TABLE IF NOT EXISTS weapons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    weapon_name TEXT,
    weapon_type TEXT NOT NULL,
    element TEXT NOT NULL,
    current_series_skill TEXT,
    current_group_skill TEXT,
    enhancement_type TEXT,
    p_bonus_1 TEXT DEFAULT 'なし',
    p_bonus_2 TEXT DEFAULT 'なし',
    p_bonus_3 TEXT DEFAULT 'なし',
    rest_1_type TEXT DEFAULT 'なし',
    rest_1_level TEXT DEFAULT 'なし',
    rest_2_type TEXT DEFAULT 'なし',
    rest_2_level TEXT DEFAULT 'なし',
    rest_3_type TEXT DEFAULT 'なし',
    rest_3_level TEXT DEFAULT 'なし',
    rest_4_type TEXT DEFAULT 'なし',
    rest_4_level TEXT DEFAULT 'なし',
    rest_5_type TEXT DEFAULT 'なし',
    rest_5_level TEXT DEFAULT 'なし',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. upgrades (SkillUpgrade)
CREATE TABLE IF NOT EXISTS upgrades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    weapon_type TEXT NOT NULL,
    element TEXT NOT NULL,
    series_skill TEXT,
    group_skill TEXT,
    remaining_count INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. trackers (RestorationTracker)
CREATE TABLE IF NOT EXISTS trackers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    weapon_id UUID REFERENCES weapons(id) ON DELETE CASCADE NOT NULL,
    remaining_count INTEGER DEFAULT 1,
    target_rest_1_type TEXT DEFAULT 'なし',
    target_rest_1_level TEXT DEFAULT 'なし',
    target_rest_2_type TEXT DEFAULT 'なし',
    target_rest_2_level TEXT DEFAULT 'なし',
    target_rest_3_type TEXT DEFAULT 'なし',
    target_rest_3_level TEXT DEFAULT 'なし',
    target_rest_4_type TEXT DEFAULT 'なし',
    target_rest_4_level TEXT DEFAULT 'なし',
    target_rest_5_type TEXT DEFAULT 'なし',
    target_rest_5_level TEXT DEFAULT 'なし',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- --- Row Level Security (RLS) ---

-- Enable RLS on all tables
ALTER TABLE weapons ENABLE ROW LEVEL SECURITY;
ALTER TABLE upgrades ENABLE ROW LEVEL SECURITY;
ALTER TABLE trackers ENABLE ROW LEVEL SECURITY;

-- Create Policies (Only owner can read/write)

-- Weapons Policies
CREATE POLICY "Users can insert their own weapons" ON weapons FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view their own weapons" ON weapons FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own weapons" ON weapons FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own weapons" ON weapons FOR DELETE USING (auth.uid() = user_id);

-- Upgrades Policies
CREATE POLICY "Users can insert their own upgrades" ON upgrades FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view their own upgrades" ON upgrades FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own upgrades" ON upgrades FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own upgrades" ON upgrades FOR DELETE USING (auth.uid() = user_id);

-- Trackers Policies
CREATE POLICY "Users can insert their own trackers" ON trackers FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can view their own trackers" ON trackers FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update their own trackers" ON trackers FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own trackers" ON trackers FOR DELETE USING (auth.uid() = user_id);

-- --- Trigger for updated_at ---
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_weapons_updated_at BEFORE UPDATE ON weapons FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_upgrades_updated_at BEFORE UPDATE ON upgrades FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_trackers_updated_at BEFORE UPDATE ON trackers FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
