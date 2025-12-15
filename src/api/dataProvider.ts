// src/api/dataProvider.ts
import { fetchUtils, HttpError } from 'react-admin';
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
const httpClient = async (url: string, options: fetchUtils.Options = {}) => {
    console.log('options ', options);
    options.credentials = 'include';

    try {
        const response = await fetchUtils.fetchJson(url, options);
        console.log('Response:', response.json);
        return response;
    } catch (error) {
        console.error('API request failed:', error);

        if (error instanceof HttpError) {
            throw error;
        }

        throw new HttpError(
            'API unavailable. Please try again later.',
            0,
            {}
        );
    }
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
    getList: async (resource: string, params: any) => {
        if (resource === 'orders') {
            const { page, perPage } = params.pagination || { page: 1, perPage: 20 };
            const rawFilters = params.filter || {};
            const filters = Object.fromEntries(
                Object.entries(rawFilters).filter(([, value]) => value !== '' && value !== undefined && value !== null)
            );

            const queryParams: Record<string, any> = {
                page,
                pageSize: perPage,
                ...filters,
            };

            const queryString = fetchUtils.queryParameters(queryParams);
            const url = `${apiUrl}/${resource}?${queryString}`;
            const response = await httpClient(url);
            const payload = response.json?.data ?? response.json ?? {};
            const records = Array.isArray(payload?.items)
                ? payload.items
                : Array.isArray(payload)
                    ? payload
                    : Array.isArray(payload?.data)
                        ? payload.data
                        : [];

            const data = records.map((record: any) => {
                const id = record?.id ?? record?.orderId ?? record?.order_id ?? record?.uuid;

                const orderId = record?.orderId ?? record?.order_id;
                const exchangeId =
                    record?.exchangeId ??
                    record?.exchange_id ??
                    record?.exchange?.id ??
                    record?.exchange?.slug ??
                    record?.exchange?.code;

                const exchangeName =
                    record?.exchange?.name ??
                    record?.exchange?.label ??
                    record?.exchange?.title ??
                    record?.exchange?.slug ??
                    record?.exchange?.code ??
                    exchangeId;

                const orderType = record?.order_type ?? record?.type;
                const direction = record?.pos_side ?? record?.position_side;
                const createdAt = record?.createdAt ?? record?.created_at;

                return id
                    ? {
                          ...record,
                          id,
                          orderId,
                          exchangeId,
                          exchangeName,
                          orderType,
                          direction,
                          createdAt,
                      }
                    : record;
            });

            const total = payload?.total ?? payload?.totalCount ?? data.length;

            return { data, total };
        }

        return baseProvider.getList(resource, params);
    },
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
