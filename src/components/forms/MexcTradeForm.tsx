import { useState } from 'react';
import { BooleanInput, NumberInput, SelectInput, TextInput } from 'react-admin';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';

const MexcTradeForm = () => {
    const theme = useTheme();
    const [side, setSide] = useState<'Buy' | 'Sell'>('Buy');
    const [marginType, setMarginType] = useState<'Cross' | 'Isolated'>('Cross');
    const [reduceOnly, setReduceOnly] = useState(false);
    const [tpSlEnabled, setTpSlEnabled] = useState(false);

    return (
        <Box display="flex" flexDirection="column" gap={2} sx={{ bgcolor: theme.palette.background.paper, p: 1.5, borderRadius: 2, boxShadow: 1 }}>
            <Typography variant="h6" gutterBottom>MEXC Trade</Typography>

            {/* Side Selector */}
            <Box>
                <Typography variant="body2" sx={{ mb: 0.5 }}>Side</Typography>
                <Box display="flex" gap={1}>
                    <Button
                        variant={side === 'Buy' ? 'contained' : 'outlined'}
                        color="success"
                        onClick={() => setSide('Buy')}
                    >
                        BUY
                    </Button>
                    <Button
                        variant={side === 'Sell' ? 'contained' : 'outlined'}
                        color="error"
                        onClick={() => setSide('Sell')}
                    >
                        SELL
                    </Button>
                </Box>
            </Box>

            {/* Margin Type and Leverage */}
            <Box display="flex" gap={2}>
                <SelectInput
                    source="marginType"
                    label="Margin Type"
                    choices={[
                        { id: 'Cross', name: 'Cross' },
                        { id: 'Isolated', name: 'Isolated' }
                    ]}
                    sx={{ flex: 1 }}
                />
                <NumberInput source="leverage" label="Leverage" min={1} sx={{ flex: 1 }} />
            </Box>

            {/* Entry Inputs */}
            <NumberInput source="price" fullWidth label="Price" />
            <NumberInput source="amount" fullWidth label="Amount" />
            <NumberInput source="volume" fullWidth label="Volume" />

            {/* Toggle Options */}
            <Box display="flex" alignItems="center" gap={2}>
                <BooleanInput
                    source="takeProfitEnabled"
                    label="TP/SL"
                    onChange={(e) => {
                        setTpSlEnabled(e.target.checked);
                        if (e.target.checked) setReduceOnly(false);
                    }}
                    checked={tpSlEnabled}
                />
                <BooleanInput
                    source="reduceOnly"
                    label="Reduce Only"
                    onChange={(e) => {
                        setReduceOnly(e.target.checked);
                        if (e.target.checked) setTpSlEnabled(false);
                    }}
                    checked={reduceOnly}
                />
            </Box>

            {/* TP/SL */}
            {tpSlEnabled && (
                <>
                    <NumberInput source="takeProfit" fullWidth label="Take Profit" />
                    <NumberInput source="stopLoss" fullWidth label="Stop Loss" />
                </>
            )}

            {/* Action Buttons */}
            <Box display="flex" gap={2}>
                <Button variant="contained" color="success" fullWidth>Buy/Long</Button>
                <Button variant="contained" color="error" fullWidth>Sell/Short</Button>
            </Box>

            {/* Footer */}
            <Box display="flex" justifyContent="space-between">
                <Box>
                    <Typography variant="body2">Margin: 0.00 USDT</Typography>
                    <Typography variant="body2">Est. Liq. Price: --</Typography>
                </Box>
                <Box>
                    <Typography variant="body2">Max Position: 0.00</Typography>
                    <Typography variant="body2">Est. Fee: --</Typography>
                </Box>
            </Box>
        </Box>
    );
};

export default MexcTradeForm;
