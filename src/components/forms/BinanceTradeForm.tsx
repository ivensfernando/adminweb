import * as React from 'react';
import { useEffect } from 'react';
import {
    TextInput,
    NumberInput,
    BooleanInput
} from 'react-admin';
import { useFormContext, useController, useWatch } from 'react-hook-form';
import { Box, Typography, Button, Slider, Grid } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { LongShortButtons } from '../LongShortButtons';
import {TpSlControls} from "../TpSlControls";

/** RHF-bound cycling button: writes to a string field */
const FormToggleButton = ({
                              name,
                              label,
                              options,
                              defaultValue,
                          }: {
    name: string;
    label: string;
    options: string[];
    defaultValue: string;
}) => {
    const { control } = useFormContext();
    const { field } = useController({ name, control, defaultValue });

    const current = field.value ?? defaultValue;
    const onClick = () => {
        const i = options.indexOf(current);
        const next = options[(i + 1) % options.length];
        field.onChange(next);
    };

    return (
        <Box sx={{ mb: 1 }}>
            <Typography variant="body2" sx={{ mb: 0.5 }}>{label}</Typography>
            <Button variant="contained" onClick={onClick} size="small" fullWidth>
                {String(current).toUpperCase()}
            </Button>
        </Box>
    );
};

/** RHF-bound tab group for order type */
const OrderTypeTabs = ({
                           name,
                           options,
                           defaultValue,
                       }: {
    name: string;
    options: string[];
    defaultValue: string;
}) => {
    const { control } = useFormContext();
    const { field } = useController({ name, control, defaultValue });

    return (
        <Box>
            <Typography variant="body2" sx={{ mb: 0.5 }}>Order Type</Typography>
            <Box display="flex" gap={1}>
                {options.map((option) => (
                    <Button
                        key={option}
                        onClick={() => field.onChange(option)}
                        sx={{
                            flex: 1,
                            height: 32,
                            bgcolor: field.value === option ? 'primary.main' : 'grey.800',
                            color: field.value === option ? 'common.white' : 'grey.300',
                            '&:hover': { bgcolor: 'primary.dark' },
                        }}
                        size="small"
                    >
                        {option}
                    </Button>
                ))}
            </Box>
        </Box>
    );
};

/** Fields that depend on orderType + RHF-bound Slider -> size */
const OrderFields = ({ orderTypeFieldName = 'orderType' }: { orderTypeFieldName?: string }) => {
    const { control } = useFormContext();
    const orderType = useWatch({ control, name: orderTypeFieldName }) as string;

    // Bind 'size' directly to RHF
    const { field: sizeField } = useController({
        name: 'size',
        control,
        defaultValue: 1, // initial percent
    });

    const sliderValue =
        typeof sizeField.value === 'number'
            ? sizeField.value
            : Number(sizeField.value || 0);

    const handleSliderChange = (_: unknown, v: number | number[]) => {
        sizeField.onChange(Array.isArray(v) ? v[0] : v);
    };

    return (
        <Box mt={2}>
            {orderType === 'Stop Limit' && (
                <NumberInput source="stopPrice" fullWidth label="Stop Price" />
            )}
            {orderType === 'Limit' && (
                <NumberInput source="price" fullWidth label="Price" />
            )}

            <Box sx={{ my: 2 }}>
                <Typography variant="body2">Size</Typography>
                <Slider
                    value={sliderValue}
                    onChange={handleSliderChange}
                    aria-labelledby="input-slider"
                    valueLabelDisplay="auto"
                    valueLabelFormat={(val) => `${val}%`}
                    min={0}
                    max={100}
                />
            </Box>

            {/* No defaultValue here; RHF controls it via useController */}
            {/* Keeping it is optional; useController already registers the field */}
            <NumberInput source="size" fullWidth sx={{ display: 'none' }} />
        </Box>
    );
};

const BinanceTradeForm = () => {
    const theme = useTheme();
    // const { control, setValue } = useFormContext();

    // Enforce mutual exclusivity between takeProfitEnabled and reduceOnly
    // const [takeProfitEnabled, reduceOnly] = useWatch({
    //     control,
    //     name: ['takeProfitEnabled', 'reduceOnly'],
    // }) as [boolean | undefined, boolean | undefined];

    // useEffect(() => {
    //     if (takeProfitEnabled && reduceOnly) {
    //         // Prefer the last toggled? Here we turn off reduceOnly if TP enabled
    //         setValue('reduceOnly', false, { shouldDirty: true });
    //     }
    // }, [takeProfitEnabled, reduceOnly, setValue]);

    // useEffect(() => {
    //     if (reduceOnly && takeProfitEnabled) {
    //         // Or if reduceOnly becomes true, ensure TP is off
    //         setValue('takeProfitEnabled', false, { shouldDirty: true });
    //     }
    // }, [reduceOnly, takeProfitEnabled, setValue]);

    const orderTypeOptions = ['Limit', 'Market', 'Stop Limit'];

    return (
        <Box
            sx={{
                bgcolor: theme.palette.background.paper,
                p: 2,
                borderRadius: 2,
                boxShadow: 1,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
            }}
        >
            <Box>
                <Typography variant="h6" gutterBottom>Binance Trade</Typography>

                <Grid container spacing={2} mb={2}>
                    <Grid {...({ item: true, xs: 12, sm: 4 } as any)}>
                        <FormToggleButton
                            name="marginMode"
                            label="Margin Mode"
                            options={['Cross', 'Isolated']}
                            defaultValue="Cross"
                        />
                    </Grid>

                    <Grid {...({ item: true, xs: 12, sm: 4 } as any)}>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>Leverage</Typography>
                        <NumberInput source="leverage" label={false} min={1} fullWidth />
                    </Grid>

                    <Grid {...({ item: true, xs: 12, sm: 4 } as any)}>
                        <FormToggleButton
                            name="assetMode"
                            label="Asset Mode"
                            options={['Single-Asset', 'Multi-Assets']}
                            defaultValue="Single-Asset"
                        />
                    </Grid>
                </Grid>

                {/* Order Type + dependent fields */}
                <Box mb={2}>
                    <OrderTypeTabs
                        name="orderType"
                        options={orderTypeOptions}
                        defaultValue="Stop Limit"
                    />
                    <OrderFields orderTypeFieldName="orderType" />
                </Box>

                <Box display="flex" alignItems="center" gap={2} my={2}>
                    <TpSlControls
                        tpEnabledSource="takeProfitEnabled"
                        reduceOnlySource="reduceOnly"
                        takeProfitSource="takeProfit"
                        stopLossSource="stopLoss"
                        buttonLabels={{ tpSl: 'TP/SL', reduceOnly: 'Reduce-Only' }}
                        fieldHeadings={{ stopLoss: 'Stop Loss', takeProfit: 'Take Profit' }} // your custom text here
                        clearOnDisable={true}
                    />
                </Box>
                {/*<Box display="flex" alignItems="center" gap={2} mt={1.5}>*/}
                {/*    /!* Let RA control these; exclusivity handled by useEffect above *!/*/}
                {/*    <BooleanInput source="takeProfitEnabled" label="TP/SL" />*/}
                {/*    <BooleanInput source="reduceOnly" label="Reduce-Only" />*/}
                {/*</Box>*/}

                {/*{takeProfitEnabled ? (*/}
                {/*    <>*/}
                {/*        <NumberInput source="takeProfit" fullWidth label="Take Profit" />*/}
                {/*        <NumberInput source="stopLoss" fullWidth label="Stop Loss" />*/}
                {/*    </>*/}
                {/*) : null}*/}
            </Box>

            <Box display="flex" gap={2} mt={3}>
                <LongShortButtons longLabel="Buy/Long" shortLabel="Sell/Short" />
            </Box>
        </Box>
    );
};

export default BinanceTradeForm;



