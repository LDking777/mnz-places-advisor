-- Habilitar PostGIS e insertar lugares clave de Manizales
CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS places CASCADE;

CREATE TABLE places (
    id SERIAL PRIMARY KEY,
    external_id TEXT UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    categories TEXT[] NOT NULL DEFAULT '{}',
    description TEXT,
    geom GEOGRAPHY(POINT, 4326) NOT NULL,
    source TEXT NOT NULL DEFAULT 'local_database',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_places_geom ON places USING GIST (geom);
CREATE INDEX idx_places_category ON places (category);
CREATE INDEX idx_places_categories ON places USING GIN (categories);

INSERT INTO places (external_id, name, category, categories, description, geom) VALUES
-- Puntos Turísticos e Históricos (tourism.sights)
('man_01', 'Catedral Basílica Metropolitana de Manizales', 'tourism.sights', ARRAY['tourism.sights', 'building.historic'], 'Plaza de Bolívar, arquitectura neogótica y recorrido guiado al Corredor Polaco.', ST_SetSRID(ST_MakePoint(-75.5169, 5.0675), 4326)::geography),
('man_02', 'Mirador de Chipre', 'tourism.sights', ARRAY['tourism.sights', 'viewpoint'], 'Avenida 12 de Octubre, atardeceres panorámicos sobre el cañón del Cauca.', ST_SetSRID(ST_MakePoint(-75.5280, 5.0689), 4326)::geography),
('man_03', 'Torre El Cable', 'tourism.sights', ARRAY['tourism.sights', 'building.historic'], 'Monumento histórico en la Plaza de Bolívar / sector El Cable, símbolo del cable aéreo histórico.', ST_SetSRID(ST_MakePoint(-75.4862, 5.0548), 4326)::geography),
('man_04', 'Monumento a los Colonizadores', 'tourism.sights', ARRAY['tourism.sights', 'artwork'], 'Ubicado en Chipre, magna obra en bronce en homenaje a la fundación de la ciudad.', ST_SetSRID(ST_MakePoint(-75.5312, 5.0695), 4326)::geography),
('man_05', 'Palacio de la Gobernación de Caldas', 'tourism.sights', ARRAY['tourism.sights', 'building.historic'], 'Edificio de arquitectura republicana en el centro de la ciudad.', ST_SetSRID(ST_MakePoint(-75.5175, 5.0678), 4326)::geography),

-- Naturaleza y Ecoparques (nature.park / natural)
('man_06', 'Recinto del Pensamiento', 'nature.park', ARRAY['nature.park', 'tourism.attraction'], 'Bosque de niebla, mariposario, avistamiento de aves y senderos ecológicos.', ST_SetSRID(ST_MakePoint(-75.4601, 5.0485), 4326)::geography),
('man_07', 'Ecoparque Los Yarumos', 'nature.park', ARRAY['nature.park', 'leisure.park'], 'Parque natural urbano, bioma de selva húmeda y actividades al aire libre.', ST_SetSRID(ST_MakePoint(-75.4925, 5.0631), 4326)::geography),
('man_08', 'Ecoparque Alcázares Arenillo', 'nature.park', ARRAY['nature.park', 'natural.forest'], 'Reserva biológica ideal para avistamiento de aves muy cerca del centro.', ST_SetSRID(ST_MakePoint(-75.5255, 5.0612), 4326)::geography),
('man_09', 'Bosque Popular El Prado', 'nature.park', ARRAY['nature.park', 'leisure.park'], 'Extenso parque recreativo con zonas verdes, instalaciones deportivas y piscinas.', ST_SetSRID(ST_MakePoint(-75.4712, 5.0415), 4326)::geography),

-- Salud, Aguas Termales y Bienestar (leisure.spa)
('man_10', 'Termales El Otoño', 'leisure.spa', ARRAY['leisure.spa', 'tourism.attraction'], 'Aguas termales geotérmicas, spa y relajación en la vía al Nevado del Ruiz.', ST_SetSRID(ST_MakePoint(-75.4411, 5.0289), 4326)::geography),
('man_11', 'Termales San Vicente (Oficina/Sede)', 'leisure.spa', ARRAY['leisure.spa'], 'Reserva de experiencias termales en entorno de reserva natural.', ST_SetSRID(ST_MakePoint(-75.4480, 5.0310), 4326)::geography),
('man_12', 'Termales Tierra Viva', 'leisure.spa', ARRAY['leisure.spa', 'tourism.attraction'], 'Termales naturales en entorno íntimo y campestre.', ST_SetSRID(ST_MakePoint(-75.4452, 5.0298), 4326)::geography),

-- Cultura y Museos (tourism.sights / entertainment)
('man_13', 'Museo de Arte de Caldas', 'tourism.sights', ARRAY['tourism.sights', 'entertainment.museum'], 'Ubicado en el Centro Cultural Universitario Rogelio Salmona.', ST_SetSRID(ST_MakePoint(-75.4931, 5.0562), 4326)::geography),
('man_14', 'Museo Arqueológico de la Universidad de Caldas', 'tourism.sights', ARRAY['tourism.sights', 'entertainment.museum'], 'Muestra prehispánica de la cultura Quimbaya y región caldense.', ST_SetSRID(ST_MakePoint(-75.4988, 5.0581), 4326)::geography),
('man_15', 'Centro Cultural Universitario Rogelio Salmona', 'tourism.sights', ARRAY['tourism.sights', 'building.architecture'], 'Joya arquitectónica moderna sede de eventos culturales y biblioteca.', ST_SetSRID(ST_MakePoint(-75.4930, 5.0560), 4326));