import React from 'react';
import {
    Datagrid,
    DateField,
    DateInput,
    FunctionField,
    List,
    NumberField,
    Pagination,
    SelectInput,
    TextField,
    TextInput,
    TopToolbar,
    useGetList,
} from 'react-admin';
import { Box, Paper } from '@mui/material';

const OrdersListActions = () => <TopToolbar />;

const normalizeExchangeChoices = (exchanges: any[] = []) => {
    const normalized = exchanges
        .map((exchange) => {
            const id =
                exchange?.id ||
                exchange?.slug ||
                exchange?.code ||
                exchange?.exchangeId ||
                exchange?.name;

            if (!id) {
                return null;
            }

            const name =
                exchange?.name || exchange?.label || exchange?.title || exchange?.code || exchange?.slug || id;

            return { id: String(id), name: String(name) };
        })
        .filter(Boolean) as { id: string; name: string }[];

    return [{ id: '', name: 'All exchanges' }, ...normalized];
};

const orderFilters = (exchangeChoices: { id: string; name: string }[]) => [
    <TextInput key="orderId" label="Order ID" source="orderId" alwaysOn />,
    <TextInput key="symbol" label="Symbol" source="symbol" alwaysOn />,
    <SelectInput
        key="exchangeId"
        label="Exchange"
        source="exchangeId"
        choices={exchangeChoices}
        optionText="name"
        optionValue="id"
        alwaysOn
        emptyValue={undefined}
        defaultValue=""
    />,
    <SelectInput
        key="order_type"
        label="Type"
        source="order_type"
        choices={[
            { id: '', name: 'All types' },
            { id: 'buy', name: 'Buy' },
            { id: 'sell', name: 'Sell' },
            { id: 'long', name: 'Long' },
            { id: 'short', name: 'Short' },
        ]}
        optionText="name"
        optionValue="id"
        emptyValue={undefined}
    />,
    <DateInput key="createdAtFrom" label="Created from" source="createdAtFrom" alwaysOn />,
    <DateInput key="createdAtTo" label="Created to" source="createdAtTo" alwaysOn />,
];

const OrdersList = () => {
    const { data: exchanges } = useGetList('lookup/exchanges');
    const exchangeChoices = normalizeExchangeChoices(exchanges ?? []);

    return (
        <Box p={2}>
            <Paper
                elevation={3}
                sx={{
                    position: 'relative',
                    paddingBottom: 3,
                    paddingTop: 3,
                    borderRadius: 2,
                    overflow: 'hidden',
                    marginTop: 4,
                }}
            >
                <List
                    title="Orders"
                    filters={orderFilters(exchangeChoices)}
                    actions={<OrdersListActions />}
                    pagination={<Pagination rowsPerPageOptions={[10, 20, 50, 100]} />}
                    perPage={20}
                    sort={{ field: 'createdAt', order: 'DESC' }}
                >
                    <Datagrid rowClick={false} bulkActionButtons={false}>
                        <DateField
                            source="createdAt"
                            label="Created"
                            showTime
                            options={{
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit',
                            }}
                        />
                        <TextField source="orderId" label="Order ID" />
                        <TextField source="uuid" label="UUID" />
                        <FunctionField
                            label="Exchange"
                            render={(record: any) => record?.exchangeName ?? record?.exchangeId ?? record?.exchange?.name ?? '-'}
                        />
                        <TextField source="symbol" label="Symbol" />
                        <TextField source="side" label="Side" />
                        <TextField source="orderType" label="Type" />
                        <TextField
                            source="direction"
                            label="Direction"
                            render={(record: any) => record?.direction ?? record?.pos_side ?? record?.position_side ?? '-'}
                        />
                        <NumberField source="price" label="Price" />
                        <NumberField source="contract_quantity" label="Qty" />
                        <NumberField source="leverage" label="Leverage" />
                        <NumberField source="pnl" label="PnL" />
                        <FunctionField
                            label="Positions"
                            render={(record: any) =>
                                Array.isArray(record?.positions)
                                    ? record.positions
                                          .map((position: any) => position?.label ?? position?.exchangeId ?? position?.id)
                                          .filter(Boolean)
                                          .join(', ')
                                    : '-'
                            }
                        />
                    </Datagrid>
                </List>
                <Box
                    sx={(theme) => ({
                        position: 'absolute',
                        bottom: 0,
                        left: 0,
                        width: '100%',
                        height: '40px',
                        bgcolor: theme.palette.mode === 'dark' ? 'blueviolet' : 'blue',
                    })}
                />
            </Paper>
        </Box>
    );
};

export default OrdersList;
