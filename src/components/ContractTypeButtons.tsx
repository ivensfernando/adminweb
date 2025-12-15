import * as React from 'react';
import { Box, Button, Typography } from '@mui/material';
import { useFormContext, useController } from 'react-hook-form';

type Option = { label: string; code: string };

interface Props {
    /** RHF field name (default: "contractType") */
    name?: string;
    /** Options shown and codes sent to backend */
    options?: Option[];
    /** Initial code if the field has no value yet */
    defaultCode?: string;
    /** Layout tweaks */
    gap?: number;
}

export const ContractTypeButtons: React.FC<Props> = ({
                                                         name = 'contractType',
                                                         // Codes as requested (note: "SPOPT" and "CORSS" kept verbatim)
                                                         options = [
                                                             { label: 'Spot',         code: 'SPOPT'   },
                                                             { label: 'Cross Margin', code: 'CORSS'   },
                                                             { label: 'Futures',      code: 'FUTURES' },
                                                         ],
                                                         defaultCode = 'FUTURES',
                                                         gap = 1,
                                                     }) => {
    const { control, setValue  } = useFormContext();
    const { field } = useController({ name, control, defaultValue: defaultCode });

    React.useEffect(() => {
        if (field.value === undefined || field.value === null) {
            setValue(name, defaultCode, { shouldDirty: false });
        }
    }, [field.value, name, defaultCode, setValue]);

    const current = field.value ?? defaultCode;

    return (
        <Box>
            <Typography variant="body2" sx={{ mb: 0.5 }}>Contract Type</Typography>
            <Box display="flex" gap={gap}>
                {options.map(({ label, code }) => {
                    const selected = current === code;
                    return (
                        <Button
                            key={code}
                            variant={selected ? 'contained' : 'outlined'}
                            onClick={() => field.onChange(code)}
                        >
                            {label.toUpperCase()}
                        </Button>
                    );
                })}
            </Box>
        </Box>
    );
};
