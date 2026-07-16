// Logo filename map — IPL franchises only (real marks live in /public/logos/)
export const TEAM_LOGOS: Record<string, string> = {
  CSK:  '/logos/CSK.svg',
  MI:   '/logos/MI.svg',
  RCB:  '/logos/RCB.svg',
  KKR:  '/logos/KKR.svg',
  DC:   '/logos/DC.svg',
  PBKS: '/logos/PBKS.svg',
  RR:   '/logos/RR.svg',
  SRH:  '/logos/SRH.svg',
  LSG:  '/logos/LSG.svg',
  GT:   '/logos/GT.svg',
  DCH:  '/logos/DCH.png',
  KTK:  '/logos/KTK.png',
  PWI:  '/logos/PWI.png',
  GL:   '/logos/GL.png',
  RPS:  '/logos/RPS.png',
  // International Teams (Real logos in /assets/logos/)
  IND:  '/assets/logos/IND.png',
  PAK:  '/assets/logos/PAK.png',
  AUS:  '/assets/logos/AUS.png',
  ENG:  '/assets/logos/ENG.png',
  RSA:  '/assets/logos/RSA.png',
  NZL:  '/assets/logos/NZL.png',
  WI:   '/assets/logos/WI.png',
  SL:   '/assets/logos/SL.png',
  AFG:  '/assets/logos/AFG.png',
  BAN:  '/assets/logos/BAN.png',
  IRE:  '/assets/logos/IRE.png',
  NED:  '/assets/logos/NED.png',
  NAM:  '/assets/logos/NAM.png',
  USA:  '/assets/logos/USA.png',
  CAN:  '/assets/logos/CAN.png',
  UGA:  '/assets/logos/UGA.png',
};

// Full name → short code, for when the backend returns human names
const TEAM_NAME_TO_CODE: Record<string, string> = {
  'Chennai Super Kings': 'CSK',
  'Mumbai Indians': 'MI',
  'Royal Challengers Bengaluru': 'RCB',
  'Royal Challengers Bangalore': 'RCB',
  'Kolkata Knight Riders': 'KKR',
  'Delhi Capitals': 'DC',
  'Punjab Kings': 'PBKS',
  'Rajasthan Royals': 'RR',
  'Sunrisers Hyderabad': 'SRH',
  'Lucknow Super Giants': 'LSG',
  'Gujarat Titans': 'GT',
  'India': 'IND',
  'Pakistan': 'PAK',
  'Australia': 'AUS',
  'England': 'ENG',
  'South Africa': 'RSA',
  'New Zealand': 'NZL',
  'West Indies': 'WI',
  'Sri Lanka': 'SL',
  'Afghanistan': 'AFG',
  'Bangladesh': 'BAN',
  'Ireland': 'IRE',
  'Netherlands': 'NED',
  'Namibia': 'NAM',
  'USA': 'USA',
  'Canada': 'CAN',
  'Uganda': 'UGA',
  // Women Variants
  'India Women': 'IND',
  'Pakistan Women': 'PAK',
  'Australia Women': 'AUS',
  'England Women': 'ENG',
  'South Africa Women': 'RSA',
  'New Zealand Women': 'NZL',
  'West Indies Women': 'WI',
  'Sri Lanka Women': 'SL',
};

export function getTeamLogo(codeOrName: string): string | undefined {
  if (TEAM_LOGOS[codeOrName]) return TEAM_LOGOS[codeOrName];
  const code = TEAM_NAME_TO_CODE[codeOrName];
  return code ? TEAM_LOGOS[code] : undefined;
}

// Team color map for all tournament types
export const TEAM_COLORS: Record<string, string> = {
  // IPL Franchises
  "CSK": "#F9CD02", "MI": "#004BA0", "RCB": "#EC1C24", "KKR": "#3A225D",
  "DC": "#00008B", "PBKS": "#ED1B24", "RR": "#2D9CDB", "SRH": "#F7A721",
  "LSG": "#A2D9CE", "GT": "#1B2A4A",
  // International Men
  "India": "#004BA0", "Australia": "#FFCD00", "England": "#CE1126",
  "South Africa": "#007A4D", "Pakistan": "#115740", "New Zealand": "#000000",
  "West Indies": "#7B121C", "Sri Lanka": "#002F6C", "Afghanistan": "#0048E0",
  "Bangladesh": "#006A4E",
  // International Women
  "India Women": "#004BA0", "Australia Women": "#FFCD00", "England Women": "#CE1126",
  "South Africa Women": "#007A4D", "Pakistan Women": "#115740", "New Zealand Women": "#000000",
  "West Indies Women": "#7B121C", "Sri Lanka Women": "#002F6C",
};

// Tournament dropdown options
export const TOURNAMENTS = [
  { value: 'ipl', label: 'IPL 2026' },
] as const;

// Shared data interfaces
export interface TeamData {
  team: string;
  prob: number;
  color: string;
  trend?: number;
  confidence?: string;
  explanation?: {
    why: string[];
    risk: string[];
  };
}

export interface ModelStat {
  name: string;
  acc: string;
  auc: string;
}

export interface ShapFeature {
  name: string;
  val: number;
}

export interface MatchFixture {
  date?: string;
  team1: string;
  team2: string;
  predicted_winner: string;
  win_probability?: number;
}

export interface IntelligenceData {
  squad_strength: Record<string, number>;
  playoff_rate: Record<string, number>;
  form_score: Record<string, number>;
}

export interface PlayerData {
  id: string;
  name: string;
  team: string;
  role: 'BAT' | 'BOWL' | 'ALL' | 'WK';
  form: number;
  impact: number;
  nationality: string;
}

export const PLAYER_DIRECTORY: PlayerData[] = [
  { id: 'p1', name: 'Rohit Sharma', team: 'MI', role: 'BAT', form: 84, impact: 91, nationality: 'IND' },
  { id: 'p2', name: 'MS Dhoni', team: 'CSK', role: 'WK', form: 71, impact: 88, nationality: 'IND' },
  { id: 'p3', name: 'Virat Kohli', team: 'RCB', role: 'BAT', form: 88, impact: 93, nationality: 'IND' },
  { id: 'p4', name: 'Andre Russell', team: 'KKR', role: 'ALL', form: 79, impact: 87, nationality: 'WI' },
  { id: 'p5', name: 'Hardik Pandya', team: 'GT', role: 'ALL', form: 81, impact: 85, nationality: 'IND' },
  { id: 'p6', name: 'Rishabh Pant', team: 'DC', role: 'WK', form: 76, impact: 82, nationality: 'IND' },
  { id: 'p7', name: 'Shikhar Dhawan', team: 'PBKS', role: 'BAT', form: 68, impact: 74, nationality: 'IND' },
  { id: 'p8', name: 'Travis Head', team: 'SRH', role: 'BAT', form: 86, impact: 84, nationality: 'AUS' },
  { id: 'p9', name: 'Sanju Samson', team: 'RR', role: 'WK', form: 78, impact: 80, nationality: 'IND' },
  { id: 'p10', name: 'KL Rahul', team: 'LSG', role: 'BAT', form: 74, impact: 79, nationality: 'IND' },
  { id: 'p11', name: 'Jasprit Bumrah', team: 'MI', role: 'BOWL', form: 90, impact: 95, nationality: 'IND' },
  { id: 'p12', name: 'Rashid Khan', team: 'GT', role: 'BOWL', form: 87, impact: 90, nationality: 'AFG' },
];

export const LEADERBOARD_DATA = {
  updatedAt: '2026-04-23',
  userStandings: [
    { rank: 1, name: 'BoundaryOracle', points: 1240, correct: 42, streak: 7, movement: 2 },
    { rank: 2, name: 'PowerplayPulse', points: 1198, correct: 40, streak: 5, movement: -1 },
    { rank: 3, name: 'YorkerMind', points: 1162, correct: 39, streak: 4, movement: 4 },
    { rank: 4, name: 'SpinLedger', points: 1115, correct: 37, streak: 3, movement: 0 },
    { rank: 5, name: 'ChaseMatrix', points: 1086, correct: 35, streak: 2, movement: -2 },
  ],
  history: [
    { week: 'W1', users: 52, models: 49 },
    { week: 'W2', users: 55, models: 52 },
    { week: 'W3', users: 58, models: 54 },
    { week: 'W4', users: 61, models: 57 },
    { week: 'W5', users: 64, models: 58 },
    { week: 'W6', users: 67, models: 60 },
  ],
};
