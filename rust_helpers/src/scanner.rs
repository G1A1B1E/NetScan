use std::net::{IpAddr, Ipv4Addr, SocketAddr, TcpStream};
use std::time::{Duration, Instant};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::net::TcpStream as AsyncTcpStream;
use tokio::time::timeout;
use tokio::sync::Semaphore;
use pyo3::prelude::*;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScanResult {
    pub ip: String,
    pub mac: String,
    pub hostname: String,
    pub vendor: String,
    pub status: String,
    pub response_time_ms: f64,
    pub open_ports: Vec<u16>,
    pub discovery_method: String,
}

impl IntoPy<PyObject> for ScanResult {
    fn into_py(self, py: Python) -> PyObject {
        let dict = pyo3::types::PyDict::new(py);
        dict.set_item("ip", self.ip).unwrap();
        dict.set_item("mac", self.mac).unwrap();
        dict.set_item("hostname", self.hostname).unwrap();
        dict.set_item("vendor", self.vendor).unwrap();
        dict.set_item("status", self.status).unwrap();
        dict.set_item("response_time_ms", self.response_time_ms).unwrap();
        dict.set_item("open_ports", self.open_ports).unwrap();
        dict.set_item("discovery_method", self.discovery_method).unwrap();
        dict.into()
    }
}

/// Fast TCP connect scan
pub async fn tcp_connect_scan(
    ip: &str,
    port: u16,
    timeout_ms: u64,
) -> Option<f64> {
    let addr: SocketAddr = format!("{}:{}", ip, port).parse().ok()?;
    let start = Instant::now();
    
    match timeout(
        Duration::from_millis(timeout_ms),
        AsyncTcpStream::connect(addr)
    ).await {
        Ok(Ok(_)) => Some(start.elapsed().as_secs_f64() * 1000.0),
        _ => None
    }
}

/// Scan multiple ports on a single host
pub async fn scan_host_ports(
    ip: &str,
    ports: &[u16],
    timeout_ms: u64,
    semaphore: Arc<Semaphore>,
) -> (String, Vec<u16>, f64) {
    let mut open_ports = Vec::new();
    let mut min_response_time = f64::MAX;
    
    for &port in ports {
        let _permit = semaphore.acquire().await.unwrap();
        
        if let Some(response_time) = tcp_connect_scan(ip, port, timeout_ms).await {
            open_ports.push(port);
            if response_time < min_response_time {
                min_response_time = response_time;
            }
        }
    }
    
    let response = if min_response_time == f64::MAX { 0.0 } else { min_response_time };
    (ip.to_string(), open_ports, response)
}

/// Batch TCP connect scan
#[pyfunction]
pub fn tcp_scan_batch(
    py: Python,
    ips: Vec<String>,
    ports: Vec<u16>,
    timeout_ms: u64,
    max_concurrent: usize,
) -> PyResult<Vec<HashMap<String, PyObject>>> {
    py.allow_threads(|| {
        let rt = tokio::runtime::Runtime::new().unwrap();
        
        rt.block_on(async {
            let semaphore = Arc::new(Semaphore::new(max_concurrent));
            let mut handles = Vec::new();
            
            for ip in ips {
                let ports = ports.clone();
                let sem = semaphore.clone();
                
                handles.push(tokio::spawn(async move {
                    scan_host_ports(&ip, &ports, timeout_ms, sem).await
                }));
            }
            
            let mut results = Vec::new();
            for handle in handles {
                if let Ok((ip, open_ports, response_time)) = handle.await {
                    if !open_ports.is_empty() {
                        let mut map = HashMap::new();
                        Python::with_gil(|py| {
                            map.insert("ip".to_string(), ip.into_py(py));
                            map.insert("open_ports".to_string(), open_ports.into_py(py));
                            map.insert("response_time_ms".to_string(), response_time.into_py(py));
                            map.insert("status".to_string(), "up".into_py(py));
                        });
                        results.push(map);
                    }
                }
            }
            
            Ok(results)
        })
    })
}

/// Fast ping sweep using raw sockets (requires root on Linux)
#[pyfunction]
pub fn ping_sweep_fast(
    py: Python,
    ips: Vec<String>,
    timeout_ms: u64,
    max_concurrent: usize,
) -> PyResult<Vec<HashMap<String, PyObject>>> {
    // Fall back to TCP ping on common ports
    let common_ports = vec![80, 443, 22, 445, 139, 21, 23, 25, 3389];
    tcp_scan_batch(py, ips, common_ports, timeout_ms, max_concurrent)
}

// Common port list for quick scans
pub const COMMON_PORTS: &[u16] = &[
    21,    // FTP
    22,    // SSH
    23,    // Telnet
    25,    // SMTP
    53,    // DNS
    80,    // HTTP
    110,   // POP3
    111,   // RPC
    135,   // MSRPC
    139,   // NetBIOS
    143,   // IMAP
    443,   // HTTPS
    445,   // SMB
    993,   // IMAPS
    995,   // POP3S
    1723,  // PPTP
    3306,  // MySQL
    3389,  // RDP
    5432,  // PostgreSQL
    5900,  // VNC
    8080,  // HTTP-Alt
    8443,  // HTTPS-Alt
];

#[pyfunction]
pub fn get_common_ports() -> Vec<u16> {
    COMMON_PORTS.to_vec()
}
