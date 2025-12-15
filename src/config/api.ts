// Base URL without any trailing slash
const RAW_API_URL = process.env.REACT_APP_API_URL?.replace(/\/$/, '') ?? '';

// Full `/api/v1` URL, ensuring the segment is present only once
export const API_V1_URL = RAW_API_URL.endsWith('/api/v1')
    ? RAW_API_URL
    : `${RAW_API_URL}/api/v1`;

// Backward compatible export used by screens that manually append `/api/v1`
export const API_URL = RAW_API_URL;
