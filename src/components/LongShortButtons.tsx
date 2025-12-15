import * as React from 'react';
import { Box, Button, ButtonProps } from '@mui/material';
import { useFormContext, useController } from 'react-hook-form';

type MuiColor = ButtonProps['color'];

export interface LongShortButtonsProps {
    /** Labels */
    longLabel?: React.ReactNode;   // default: "Buy/Long"
    shortLabel?: React.ReactNode;  // default: "Sell/Short"

    /** Field names in your form data */
    longName?: string;  // default: "isLong"
    shortName?: string; // default: "isShort"

    /** MUI colors */
    longColor?: MuiColor;  // default: "success"
    shortColor?: MuiColor; // default: "error"

    /** UI tweaks */
    allowUnset?: boolean;  // click selected again to clear; default: true
    fullWidth?: boolean;   // default: true
    gap?: number | string; // default: 2
    mt?: number | string;  // default: 3
}

export const LongShortButtons: React.FC<LongShortButtonsProps> = ({
                                                                      longLabel = 'Buy/Long',
                                                                      shortLabel = 'Sell/Short',
                                                                      longName = 'isLong',
                                                                      shortName = 'isShort',
                                                                      longColor = 'success',
                                                                      shortColor = 'error',
                                                                      allowUnset = true,
                                                                      fullWidth = true,
                                                                      gap = 2,
                                                                      mt = 3,
                                                                  }) => {
    const { control } = useFormContext();

    const {
        field: { value: isLong = false, onChange: setIsLong },
    } = useController({ name: longName, control, defaultValue: false });

    const {
        field: { value: isShort = false, onChange: setIsShort },
    } = useController({ name: shortName, control, defaultValue: false });

    const toggleLong = () => {
        if (isLong && allowUnset) setIsLong(false);
        else {
            setIsLong(true);
            setIsShort(false);
        }
    };

    const toggleShort = () => {
        if (isShort && allowUnset) setIsShort(false);
        else {
            setIsShort(true);
            setIsLong(false);
        }
    };

    return (
        <Box display="flex" gap={gap} mt={mt}>
            <Button
                type="button"
                variant={isLong ? 'contained' : 'outlined'}
                color={longColor}
                fullWidth={fullWidth}
                onClick={toggleLong}
                aria-pressed={isLong}
            >
                {longLabel}
            </Button>

            <Button
                type="button"
                variant={isShort ? 'contained' : 'outlined'}
                color={shortColor}
                fullWidth={fullWidth}
                onClick={toggleShort}
                aria-pressed={isShort}
            >
                {shortLabel}
            </Button>
        </Box>
    );
};
