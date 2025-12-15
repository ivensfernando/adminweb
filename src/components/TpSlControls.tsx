import * as React from 'react';
import { Box, Typography } from '@mui/material';
import { BooleanInput, NumberInput } from 'react-admin';
import { useFormContext, useWatch } from 'react-hook-form';

type Props = {
    tpEnabledSource?: string;
    reduceOnlySource?: string;
    takeProfitSource?: string;
    stopLossSource?: string;
    clearOnDisable?: boolean;
    stickToBottom?: boolean;     // <<— pushes this block to the bottom of its flex column parent
    buttonLabels?: { tpSl?: string; reduceOnly?: string };
    fieldHeadings?: { stopLoss?: string; takeProfit?: string };
};

export const TpSlControls: React.FC<Props> = ({
                                                  tpEnabledSource = 'takeProfitEnabled',
                                                  reduceOnlySource = 'reduceOnly',
                                                  takeProfitSource = 'takeProfit',
                                                  stopLossSource = 'stopLoss',
                                                  clearOnDisable = true,
                                                  stickToBottom = true,
                                                  buttonLabels = { tpSl: 'TP/SL', reduceOnly: 'Reduce-Only' },
                                                  fieldHeadings = { stopLoss: 'Stop Loss', takeProfit: 'Take Profit' },
                                              }) => {
    const { control, setValue, clearErrors } = useFormContext();
    const [tpEnabled = false, reduceOnly = false] = useWatch({
        control,
        name: [tpEnabledSource, reduceOnlySource],
    }) as [boolean | undefined, boolean | undefined];

    // ---- Mutual exclusivity without flapping (keep the one just turned ON)
    const prev = React.useRef({ tp: !!tpEnabled, ro: !!reduceOnly });
    React.useEffect(() => {
        const tp = !!tpEnabled;
        const ro = !!reduceOnly;

        const tpRising = !prev.current.tp && tp; // false -> true
        const roRising = !prev.current.ro && ro; // false -> true

        if (tpRising && ro) {
            setValue(reduceOnlySource, false, { shouldDirty: true });
        } else if (roRising && tp) {
            setValue(tpEnabledSource, false, { shouldDirty: true });
        }

        prev.current = { tp, ro };
    }, [tpEnabled, reduceOnly, setValue, reduceOnlySource, tpEnabledSource]);

    // ---- Clear numbers when TP/SL disabled
    React.useEffect(() => {
        if (!tpEnabled && clearOnDisable) {
            setValue(takeProfitSource, undefined, { shouldDirty: true, shouldValidate: true });
            setValue(stopLossSource, undefined, { shouldDirty: true, shouldValidate: true });
            clearErrors?.([takeProfitSource, stopLossSource] as any);
        }
    }, [tpEnabled, clearOnDisable, setValue, clearErrors, takeProfitSource, stopLossSource]);

    // Conditional validators (only when TP enabled)
    const requiredIfTp = (msg = 'Required when TP/SL is on') => (v: any) =>
        !tpEnabled ? undefined : v == null || v === '' ? msg : undefined;
    const positiveIfTp = (msg = 'Must be > 0') => (v: any) =>
        !tpEnabled ? undefined : Number(v) > 0 ? undefined : msg;
    const validators = tpEnabled ? [requiredIfTp(), positiveIfTp()] : [];

    // // mutual exclusivity
    // React.useEffect(() => {
    //     if (tpEnabled && reduceOnly) setValue(reduceOnlySource, false, { shouldDirty: true });
    // }, [tpEnabled, reduceOnly, setValue, reduceOnlySource]);
    // React.useEffect(() => {
    //     if (reduceOnly && tpEnabled) setValue(tpEnabledSource, false, { shouldDirty: true });
    // }, [reduceOnly, tpEnabled, setValue, tpEnabledSource]);
    //
    // // clear numbers when disabled
    // React.useEffect(() => {
    //     if (!tpEnabled && clearOnDisable) {
    //         setValue(takeProfitSource, undefined, { shouldDirty: true, shouldValidate: true });
    //         setValue(stopLossSource, undefined, { shouldDirty: true, shouldValidate: true });
    //         clearErrors?.([takeProfitSource, stopLossSource] as any);
    //     }
    // }, [tpEnabled, clearOnDisable, setValue, clearErrors, takeProfitSource, stopLossSource]);
    //
    // const requiredIfTp = (msg = 'Required when TP/SL is on') => (v: any) =>
    //     !tpEnabled ? undefined : (v == null || v === '' ? msg : undefined);
    // const positiveIfTp = (msg = 'Must be > 0') => (v: any) =>
    //     !tpEnabled ? undefined : (Number(v) > 0 ? undefined : msg);
    // const validators = tpEnabled ? [requiredIfTp(), positiveIfTp()] : [];

    return (
        <Box sx={{ mt: stickToBottom ? 'auto' : 0 }}>
            {/* Buttons row */}
            <Box display="flex" alignItems="center" gap={2} mt={1.5}>
                <BooleanInput source={tpEnabledSource} label={buttonLabels.tpSl} />
                <BooleanInput source={reduceOnlySource} label={buttonLabels.reduceOnly} />
            </Box>

            {/* Stacked fields BELOW the buttons */}
            {tpEnabled && (
                <Box mt={1.5} display="flex" flexDirection="column" gap={1.5}>
                    <Box>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                            {fieldHeadings.stopLoss}
                        </Typography>
                        <NumberInput source={stopLossSource} fullWidth label={false} min={0} validate={validators} />
                    </Box>

                    <Box>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                            {fieldHeadings.takeProfit}
                        </Typography>
                        <NumberInput source={takeProfitSource} fullWidth label={false} min={0} validate={validators} />
                    </Box>
                </Box>
            )}
        </Box>
    );
};
