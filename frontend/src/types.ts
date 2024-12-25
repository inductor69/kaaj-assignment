export interface Principal {
  name: string;
  title: string;
  address: string;
}

export interface RegisteredAgent {
  name: string;
  address: string;
}

export interface Business {
  id: number;
  name: string;
  status: string;
  filing_date: string;
  principals: Principal[];
  registered_agent: RegisteredAgent;
  created_at: string;
  updated_at: string;
} 