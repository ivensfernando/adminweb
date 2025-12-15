import { useState } from 'react';
import { BooleanInput, NumberInput, SelectInput, TextInput } from 'react-admin';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { useTheme } from '@mui/material/styles';
import {LongShortButtons} from "../LongShortButtons";
import * as React from "react";
import {TpSlControls} from "../TpSlControls";
import {useFormContext, useWatch} from "react-hook-form";

// Spot Subform
const SpotKucoinForm = () => (
    <Box>
        <Typography variant="body2" sx={{ mb: 1 }}>Available: 27.59397553 USDT</Typography>
        <NumberInput source="price" fullWidth label="Price" />
        <NumberInput source="amount" fullWidth label="Amount" />
        <Box display="flex" justifyContent="space-between" gap={1} my={2}>
            {[25, 50, 75, 100].map(percent => (
                <Button key={percent} size="small" variant="outlined" sx={{ flex: 1 }}>
                    {percent}%
                </Button>
            ))}
        </Box>
        <NumberInput source="volume" fullWidth label="Volume" />
        <Typography variant="body2" sx={{ mt: 1 }}>Advanced:--</Typography>
        <Box display="flex" gap={2} mt={3}>
            <LongShortButtons longLabel="Buy" shortLabel="Sell" />
        </Box>
    </Box>
);

// Cross Margin Subform
const CrossMarginKucoinForm = () => (
    <Box>
        <Typography variant="body2" sx={{ mb: 1 }}>Available: 78.90587272 USDT</Typography>
        <SelectInput source="borrowMode" label="Borrow Mode" choices={[
            { id: 'Standard', name: 'Standard' },
            { id: 'Auto-Borrow', name: 'Auto-Borrow' },
            { id: 'Auto-Repay', name: 'Auto-Repay' },
            { id: 'Auto-Borrow and Repay', name: 'Auto-Borrow and Repay' },
        ]} fullWidth />
        <NumberInput source="price" fullWidth label="Price" />
        <NumberInput source="amount" fullWidth label="Amount" />
        <Box display="flex" justifyContent="space-between" gap={1} my={2}>
            {[25, 50, 75, 100].map(percent => (
                <Button key={percent} size="small" variant="outlined" sx={{ flex: 1 }}>
                    {percent}%
                </Button>
            ))}
        </Box>
        <NumberInput source="volume" fullWidth label="Volume" />
        <Typography variant="body2" sx={{ mt: 1 }}>Advanced:--</Typography>
        <Box display="flex" gap={2} mt={3}>
            <LongShortButtons longLabel="Buy" shortLabel="Sell" />
        </Box>
    </Box>
);

// Futures Subform
const FuturesKucoinForm = () => (
    <Box>
        <Typography variant="body2" sx={{ mb: 1 }}>Assets: 70.32 USDT</Typography>

        <Box display="flex" gap={1} mb={2}>
            <SelectInput source="marginType" label="Margin Type" choices={[
                { id: 'Isolated', name: 'Isolated' },
                { id: 'Cross', name: 'Cross' }
            ]} sx={{ flex: 1 }} />

            <NumberInput source="leverage" label="Leverage" min={1} sx={{ flex: 1 }} />
        </Box>

        <NumberInput source="price" fullWidth label="Price" />
        <NumberInput source="amount" fullWidth label="Amount" />

        <Box display="flex" justifyContent="space-between" gap={1} my={2}>
            {[25, 50, 75, 100].map(percent => (
                <Button key={percent} size="small" variant="outlined" sx={{ flex: 1 }}>
                    {percent}%
                </Button>
            ))}
        </Box>

        <Typography variant="body2" sx={{ mt: 1, mb: 0.5 }}>Assets</Typography>
        <Box display="flex" justifyContent="space-between">
            <Typography variant="body2">Max Long 0.016 BTC</Typography>
            <Typography variant="body2">Max Short 0.016 BTC</Typography>
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

        {/*<Box display="flex" gap={2} mt={2}>*/}
        {/*    <Button variant="contained" color="success" fullWidth>Buy/Long</Button>*/}
        {/*    <Button variant="contained" color="error" fullWidth>Sell/Short</Button>*/}
        {/*</Box>*/}
        <Box display="flex" gap={2} mt={3}>
            <LongShortButtons longLabel="Buy/Long" shortLabel="Sell/Short" />
        </Box>

        <Box display="flex" justifyContent="space-between" mt={2}>
            <Box>
                <Typography variant="body2">Margin 0.00 USDT</Typography>
                <Typography variant="body2">Est. Liquidation Price --</Typography>
            </Box>
            <Box>
                <Typography variant="body2">Margin 0.00 USDT</Typography>
                <Typography variant="body2">Est. Liquidation Price --</Typography>
            </Box>
        </Box>
    </Box>
);

type ContractTypeCode = 'SPOPT' | 'CORSS' | 'FUTURES';

const codeToLabel: Record<ContractTypeCode, string> = {
    SPOPT: 'Spot',
    CORSS: 'Cross Margin',
    FUTURES: 'Futures',
};

// Kucoin main panel
// const KucoinTradeForm = () => {
//     const theme = useTheme();
//     const [contractType, setContractType] = useState('Spot');
//     const [side, setSide] = useState('Buy');
//
//     const contractForms: Record<string, React.ReactElement> = {
//         'Spot': <SpotKucoinForm />,
//         'Cross Margin': <CrossMarginKucoinForm />,
//         'Futures': <FuturesKucoinForm />
//     };
//
//     return (
//         <Box display="flex" flexDirection="column" gap={2} sx={{ bgcolor: theme.palette.background.paper, p: 1.5, borderRadius: 2, boxShadow: 1 }}>
//             <Typography variant="h6" gutterBottom>Kucoin Trade</Typography>
//
//             <Box>
//                 <Typography variant="body2" sx={{ mb: 0.5 }}>Contract Type</Typography>
//                 <Box display="flex" gap={1}>
//                     {['Spot', 'Cross Margin', 'Futures'].map(opt => (
//                         <Button
//                             key={opt}
//                             variant={contractType === opt ? 'contained' : 'outlined'}
//                             onClick={() => setContractType(opt)}
//                         >
//                             {opt.toUpperCase()}
//                         </Button>
//                     ))}
//                 </Box>
//             </Box>
//
//
//             {contractForms[contractType]}
//         </Box>
//     );
// };

const KucoinTradeForm: React.FC = () => {
    const theme = useTheme();
    const { control } = useFormContext();

    // Read the value set by <ContractTypeButtons />
    const contractType = useWatch({
        control,
        name: 'contractType',
        defaultValue: 'FUTURES',
    }) as ContractTypeCode;

    const contractForms: Record<ContractTypeCode, React.ReactElement> = {
        SPOPT: <SpotKucoinForm />,
        CORSS: <CrossMarginKucoinForm />,
        FUTURES: <FuturesKucoinForm />,
    };

    return (
        <Box
            display="flex"
            flexDirection="column"
            gap={2}
            sx={{ bgcolor: theme.palette.background.paper, p: 1.5, borderRadius: 2, boxShadow: 1 }}
        >
            <Typography variant="h6" gutterBottom>Kucoin Trade</Typography>

            {/* Optional: show which contract type is active */}
            <Typography variant="body2" color="text.secondary">
                Contract Type: {codeToLabel[contractType]}
            </Typography>

            {contractForms[contractType] ?? contractForms.FUTURES}
        </Box>
    );
};

export default KucoinTradeForm;
