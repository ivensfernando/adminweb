import {
    Create,
    SimpleForm,
    TextInput,
    NumberInput,
    DateInput,
    required,
    useNotify,
    useRedirect,
    useCreate,
    SelectInput,
    BooleanInput
} from 'react-admin';
import { useFormContext } from 'react-hook-form';
import Box from '@mui/material/Box';
import { Grid } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useState } from 'react';

import BinanceTradeForm from '../../components/forms/BinanceTradeForm';
import KucoinTradeForm from "../../components/forms/KucoinTradeForm";
import MexcTradeForm from "../../components/forms/MexcTradeForm";
import TradeDetailsForm from "../../components/forms/TradeDetailsForm";
import { useGetList } from 'react-admin';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import {ContractTypeButtons} from "../../components/ContractTypeButtons";



const TopFormPanel = () => {
    const { data: exchanges, isLoading: exchangesLoading } = useGetList('lookup/exchanges');
    const { data: pairs, isLoading: pairsLoading } = useGetList('lookup/pairs');
    const [contractType, setContractType] = useState('Futures');

    return (
        <Box mb={2}>
            <Grid container spacing={2}>
                <Grid {...({ item: true, xs: 12, sm: 4 } as any)}>
                    {exchangesLoading ? (
                        <CircularProgress size={24} />
                    ) : (
                        <SelectInput
                            source="exchange"
                            label="Exchange"
                            choices={exchanges || []}
                            defaultValue="Binance"
                            optionText="name"
                            optionValue="name"
                            fullWidth
                            validate={required()}
                        />
                    )}
                </Grid>
                <Grid {...({ item: true, xs: 12, sm: 4 } as any)}>
                    {pairsLoading ? (
                        <CircularProgress size={24} />
                    ) : (
                        <SelectInput
                            source="symbol"
                            label="Symbol"
                            choices={pairs || []}
                            optionText="display"
                            optionValue="display"
                            fullWidth
                            validate={required()}
                        />
                    )}
                </Grid>
                <Grid {...({ item: true, xs: 12, sm: 4 } as any)}>
                    <DateInput source="tradeDate" label="Trade Date" defaultValue={new Date()} fullWidth />
                </Grid>
                <Grid {...({ item: true, xs: 12, sm: 3 } as any)}>
                    <TextInput
                        source="tradeTime"
                        label="Trade Time"
                        type="time"
                        fullWidth
                        defaultValue="12:00"
                        InputLabelProps={{ shrink: true }}
                    />
                </Grid>

                {/* Contract Type (writes "contractType" with codes to the form) */}
                <Grid {...({ item: true, xs: 12, sm: 9 } as any)}>
                    <ContractTypeButtons
                        // optional: you can override options/codes here if needed
                        // options={[
                        //   { label: 'Spot', code: 'SPOPT' },
                        //   { label: 'Cross Margin', code: 'CORSS' },
                        //   { label: 'Futures', code: 'FUTURES' },
                        // ]}
                        defaultCode="FUTURES"
                    />
                </Grid>

            </Grid>
        </Box>
    )
};

const TradePanelBody = () => {
    const { watch } = useFormContext();
    const exchange = watch('exchange') || 'Binance';
    console.log(exchange);
    return (
        <Grid container spacing={2}>
            <Grid {...({ item: true, xs: 12, md: 6 } as any)}>
                {exchange === 'KuCoin' ? (
                    <KucoinTradeForm />
                ) : exchange === 'MEXC' ? (
                    <MexcTradeForm />
                ) : (
                    <BinanceTradeForm />
                )}
            </Grid>
            <Grid {...({ item: true, xs: 12, sm: 6 } as any)} sx={{ flexGrow: 1 }}>
                <TradeDetailsForm />
            </Grid>
        </Grid>
    );
};

const TradeCreate = () => {
    const notify = useNotify();
    const redirect = useRedirect();
    const [create] = useCreate();

    const onSave = (data: any) => {
        console.log(data);
        create('trades', { data }, {
            onSuccess: () => {
                notify('Trade created successfully');
                redirect('/trades');
            }
        });
    };

    return (
        <Create>
            <SimpleForm
                defaultValues={{ contractType: 'FUTURES' }}
                onSubmit={onSave}
            >
                <TopFormPanel />
                <TradePanelBody />
            </SimpleForm>
        </Create>
    );
};

export default TradeCreate;
