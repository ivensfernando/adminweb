// src/api/dataProvider.ts
import { fetchUtils } from 'react-admin';
// import simpleRestProvider from 'ra-data-simple-rest';
import jsonServerProvider from 'ra-data-json-server';
import { API_V1_URL } from '../config/api';

const apiUrl = API_V1_URL; // Base API URL should already include /api/v1
const apiRootUrl = apiUrl.replace(/\/api\/v1\/?$/, '');

// const httpClient = (url: string, options: fetchUtils.Options = {}) => {
//     const token = localStorage.getItem('auth_token');
//     options.user = {
//         authenticated: true,
//         token: `Bearer ${token}`,
//     };
//     return fetchUtils.fetchJson(url, options);
// };

// 👇 This wrapper adds `credentials: 'include'` to every fetch call
const httpClient = (url: string, options: fetchUtils.Options = {}) => {
    console.log('options ',options);
    options.credentials = 'include';
    return fetchUtils.fetchJson(url, options).then((res) => {
        console.log('Response:', res.json);
        return res;
    });
};

// const httpClient = (url, options = {}) => {
//     return fetchUtils.fetchJson(url, options).then((res) => {
//         console.log('Response:', res.json);
//         return res;
//     });
// };

const baseProvider = jsonServerProvider(apiUrl, httpClient);

const dataProvider = {
    ...baseProvider,
    create: async (resource: string, params: any) => {
        const res = await httpClient(`${apiUrl}/${resource}`, {
            method: 'POST',
            body: JSON.stringify(params.data),
        });

        if (resource === 'webhooks') {
            const webhook = res.json.webhook ?? res.json.data ?? res.json;
            const token = res.json.token ?? webhook?.token;
            const baseUrl = res.json.url ?? `${apiRootUrl}/trading/webhook`;
            const sanitizedBaseUrl = baseUrl?.replace(/\/$/, '');
            const fullUrl = token && sanitizedBaseUrl
                ? `${sanitizedBaseUrl}/${token}`
                : sanitizedBaseUrl;

            return {
                data: {
                    ...webhook,
                    token,
                    url: sanitizedBaseUrl,
                    fullUrl,
                },
            };
        }

        if (res.json?.data) {
            return { data: res.json.data }; // ✅ critical
        }

        return { data: res.json };
    },
    getOne: async (resource: string, params: any) => {
        const response = await httpClient(`${apiUrl}/${resource}/${params.id}`);
        const payload = response.json?.data ?? response.json;
        return { data: payload }; // ✅ must return `data` object
    },
};

// const dataProvider = simpleRestProvider(apiUrl, httpClient);
export default dataProvider;
