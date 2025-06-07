export interface MonitoringStatus {
  content_length: number;
  response_time_ms: number;
  server: string;
  status: string;
  status_code: number;
}

export interface SslInfo {
  issuer: string | null;
  valid_from: string;
  valid_until: string;
}

export interface MonitorResponse {
  alerts_triggered: any[]; // You can define a specific interface if needed
  domain_expiry: string | null;
  log_saved: boolean;
  monitoring_status: MonitoringStatus;
  ssl_info: SslInfo;
  url: string;
}
