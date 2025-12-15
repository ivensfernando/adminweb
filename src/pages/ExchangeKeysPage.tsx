import { useEffect, useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    CardHeader,
    Checkbox,
    CircularProgress,
    FormControlLabel,
    InputAdornment,
    Button,
    TextField,
    Typography,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions
} from '@mui/material';
import { Visibility, VisibilityOff, Close as CloseIcon } from '@mui/icons-material';
import { useGetList, useNotify } from 'react-admin';
import { API_V1_URL } from '../config/api';

type FieldName = 'apiKey' | 'apiSecret' | 'apiPassphrase';

type VisibilityState = Record<string, Partial<Record<FieldName, boolean>>>;

type FormValues = {
    apiKey: string;
    apiSecret: string;
    apiPassphrase: string;
    runOnServer: boolean;
};

type SavingState = Record<string, boolean>;

type ExchangeCredentialsMetadata = {
    hasApiKey: boolean;
    hasApiSecret: boolean;
    hasApiPassphrase: boolean;
};

type ValidationErrors = Record<string, Partial<Record<FieldName, string>>>;

const toSnakeCase = (value: string) => value.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);

const getDefaultFormValues = (): FormValues => ({
    apiKey: '',
    apiSecret: '',
    apiPassphrase: '',
    runOnServer: false

});

const ExchangeKeysPage = () => {
    const { data: exchanges, isLoading: exchangesLoading } = useGetList('lookup/exchanges');
    const notify = useNotify();
    const [fieldVisibility, setFieldVisibility] = useState<VisibilityState>({});
    const [formValues, setFormValues] = useState<Record<string, FormValues>>({});
    const [existingData, setExistingData] = useState<Record<string, boolean>>({});
    const [userExchangesLoading, setUserExchangesLoading] = useState<boolean>(true);
    const [savingState, setSavingState] = useState<SavingState>({});
    const [deletingState, setDeletingState] = useState<SavingState>({});
    const [testingState, setTestingState] = useState<SavingState>({});
    const [testModalState, setTestModalState] = useState<{ open: boolean; title: string; message: string }>({
        open: false,
        title: '',
        message: ''
    });
    const [credentialsMetadata, setCredentialsMetadata] = useState<Record<string, ExchangeCredentialsMetadata>>({});
    const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

    const toggleVisibility = (exchangeKey: string, field: FieldName) => {
        setFieldVisibility((prev) => ({
            ...prev,
            [exchangeKey]: {
                ...prev[exchangeKey],
                [field]: !prev[exchangeKey]?.[field]
            }
        }));
    };

    const exchangeList = exchanges ?? [];

    useEffect(() => {
        let isMounted = true;

        const extractValue = (entry: any, key: string): any => {
            if (!entry) {
                return undefined;
            }
            const candidates = [key, toSnakeCase(key), key.toUpperCase()];
            for (const candidate of candidates) {
                if (entry[candidate] !== undefined && entry[candidate] !== null) {
                    return entry[candidate];
                }
            }
            if (entry.fields && Array.isArray(entry.fields)) {
                const fieldMatch = entry.fields.find((field: any) => {
                    const fieldName = field?.name ?? field?.key ?? field?.id;
                    if (!fieldName) {
                        return false;
                    }
                    const normalized = String(fieldName).toLowerCase();
                    return normalized === key.toLowerCase() || normalized === toSnakeCase(key);
                });
                if (fieldMatch) {
                    return fieldMatch.value ?? fieldMatch.defaultValue ?? fieldMatch.initialValue ?? '';
                }
            }
            if (entry.credentials) {
                return extractValue(entry.credentials, key);
            }
            return undefined;
        };

        const normalizeExchangeKey = (entry: any) => {
            const candidates = [
                entry?.exchangeId,
                entry?.exchangeID,
                entry?.exchange_id,
                entry?.exchange?.id,
                entry?.exchange?.exchangeId,
                entry?.exchange?.slug,
                entry?.exchange?.code,
                entry?.exchange?.name,
                entry?.id
            ];

            for (const candidate of candidates) {
                if (candidate !== undefined && candidate !== null && candidate !== '') {
                    return String(candidate);
                }
            }
            return undefined;
        };

        const parseBoolean = (value: any): boolean => {
            console.log("parseBoolean",value);
            if (typeof value === 'boolean') {
                console.log("typeof value === 'boolean'")
                return value;
            }
            if (typeof value === 'string') {
                console.log("typeof value === 'string'")
                const normalized = value.trim().toLowerCase();
                return ['true', '1', 'yes', 'on'].includes(normalized);
            }
            if (typeof value === 'number') {
                console.log("typeof value === 'number'")
                return value === 1;
            }
            console.log("return false;")
            return false;
        };

        const fetchUserExchanges = async () => {
            setUserExchangesLoading(true);
            try {
                const response = await fetch(`${API_V1_URL}/user-exchanges/forms`, {
                    method: 'GET',
                    credentials: 'include'
                });

                if (!response.ok) {
                    throw new Error(`Failed to load user exchanges (${response.status})`);
                }

                const payload = await response.json();
                const items = Array.isArray(payload) ? payload : payload?.data ?? [];

                if (!isMounted) {
                    return;
                }

                const nextFormValues: Record<string, FormValues> = {};
                const nextExisting: Record<string, boolean> = {};
                const nextMetadata: Record<string, ExchangeCredentialsMetadata> = {};

                items.forEach((entry: any) => {
                    const exchangeKey = normalizeExchangeKey(entry);
                    if (!exchangeKey) {
                        return;
                    }

                    const apiKey = extractValue(entry, 'apiKey') ?? '';
                    const apiSecret = extractValue(entry, 'apiSecret') ?? '';
                    const apiPassphrase = extractValue(entry, 'apiPassphrase') ?? '';
                    const showInFormsValue = extractValue(entry, 'showInForms');
                    const runOnServerValue = extractValue(entry, 'runOnServer');
                    const hasApiKey = parseBoolean(extractValue(entry, 'hasApiKey'));
                    const hasApiSecret = parseBoolean(extractValue(entry, 'hasApiSecret'));
                    const hasApiPassphrase = parseBoolean(extractValue(entry, 'hasApiPassphrase'));
                    const runOnServer =  extractValue(entry, 'runOnServer');
                    // parseBoolean(showInFormsValue ?? runOnServerValue);

                    nextFormValues[exchangeKey] = {
                        apiKey: String(apiKey ?? ''),
                        apiSecret: String(apiSecret ?? ''),
                        apiPassphrase: String(apiPassphrase ?? ''),
                        runOnServer
                    };

                    nextMetadata[exchangeKey] = {
                        hasApiKey,
                        hasApiSecret,
                        hasApiPassphrase
                    };

                    nextExisting[exchangeKey] = Boolean(
                        hasApiKey ||
                        hasApiSecret ||
                        hasApiPassphrase ||
                        runOnServerValue
                    );
                });

                setFormValues((prev) => ({ ...prev, ...nextFormValues }));
                setExistingData(nextExisting);
                setCredentialsMetadata(nextMetadata);
            } catch (error) {
                console.error(error);
                notify('Failed to load saved exchange keys', { type: 'warning' });
                if (isMounted) {
                    setExistingData({});
                    setCredentialsMetadata({});
                }
            } finally {
                if (isMounted) {
                    setUserExchangesLoading(false);
                }
            }
        };

        fetchUserExchanges();

        return () => {
            isMounted = false;
        };
    }, [notify]);

    const handleInputChange = (exchangeKey: string, field: FieldName, value: string) => {
        setFormValues((prev) => {
            const current = { ...getDefaultFormValues(), ...prev[exchangeKey] };
            return {
                ...prev,
                [exchangeKey]: {
                    ...current,
                    [field]: value
                }
            };
        });
        setValidationErrors((prev) => {
            if (!prev[exchangeKey]?.[field]) {
                return prev;
            }
            const nextErrors = { ...prev };
            const fieldErrors = { ...(nextErrors[exchangeKey] ?? {}) };
            delete fieldErrors[field];
            if (Object.keys(fieldErrors).length === 0) {
                delete nextErrors[exchangeKey];
            } else {
                nextErrors[exchangeKey] = fieldErrors;
            }
            return nextErrors;
        });
    };

    const handleCheckboxChange = (exchangeKey: string, checked: boolean) => {
        setFormValues((prev) => {
            const current = { ...getDefaultFormValues(), ...prev[exchangeKey] };
            return {
                ...prev,
                [exchangeKey]: {
                    ...current,
                    runOnServer: checked
                }
            };
        });
    };

    const handleSave = async (exchangeKey: string, exchangeId: string | number) => {
        const values = { ...getDefaultFormValues(), ...formValues[exchangeKey] };
        const metadata = credentialsMetadata[exchangeKey] ?? {
            hasApiKey: false,
            hasApiSecret: false,
            hasApiPassphrase: false
        };

        const trimmedApiKey = values.apiKey.trim();
        const trimmedApiSecret = values.apiSecret.trim();
        const trimmedApiPassphrase = values.apiPassphrase.trim();

        const errors: Partial<Record<FieldName, string>> = {};

        if (!trimmedApiKey && !metadata.hasApiKey) {
            errors.apiKey = 'API Key is required.';
        }

        if (!trimmedApiSecret && !metadata.hasApiSecret) {
            errors.apiSecret = 'API Secret is required.';
        }

        if (Object.keys(errors).length > 0) {
            setValidationErrors((prev) => ({ ...prev, [exchangeKey]: errors }));
            notify('Please resolve the highlighted errors before saving.', { type: 'warning' });
            return;
        }

        setValidationErrors((prev) => {
            if (!prev[exchangeKey]) {
                return prev;
            }
            const next = { ...prev };
            delete next[exchangeKey];
            return next;
        });

        setSavingState((prev) => ({ ...prev, [exchangeKey]: true }));

        const payload: Record<string, any> = {
            exchangeId,
            runOnServer: values.runOnServer
        };

        if (trimmedApiKey) {
            payload.apiKey = trimmedApiKey;
        }

        if (trimmedApiSecret) {
            payload.apiSecret = trimmedApiSecret;
        }

        if (trimmedApiPassphrase) {
            payload.apiPassphrase = trimmedApiPassphrase;
        }

        try {
            const response = await fetch(`${API_V1_URL}/user-exchanges`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Failed to save exchange credentials (${response.status})`);
            }

            const updatedMetadata: ExchangeCredentialsMetadata = {
                hasApiKey: metadata.hasApiKey || Boolean(trimmedApiKey),
                hasApiSecret: metadata.hasApiSecret || Boolean(trimmedApiSecret),
                hasApiPassphrase: metadata.hasApiPassphrase || Boolean(trimmedApiPassphrase)
            };

            setCredentialsMetadata((prev) => ({
                ...prev,
                [exchangeKey]: updatedMetadata
            }));

            setExistingData((prev) => ({
                ...prev,
                [exchangeKey]: Boolean(
                    updatedMetadata.hasApiKey ||
                    updatedMetadata.hasApiSecret ||
                    updatedMetadata.hasApiPassphrase ||
                    values.runOnServer
                )
            }));

            setFormValues((prev) => ({
                ...prev,
                [exchangeKey]: {
                    ...values,
                    apiKey: '',
                    apiSecret: '',
                    apiPassphrase: '',
                    runOnServer: values.runOnServer
                }
            }));

            notify('Exchange credentials saved successfully', { type: 'info' });
        } catch (error) {
            console.error(error);
            notify('Failed to save exchange credentials', { type: 'error' });
        } finally {
            setSavingState((prev) => ({ ...prev, [exchangeKey]: false }));
        }
    };

    const handleClear = async (exchangeKey: string, exchangeId: string | number) => {
        const confirmation = window.confirm('Do you really want to delete these credentials?');
        if (!confirmation) {
            return;
        }

        setDeletingState((prev) => ({ ...prev, [exchangeKey]: true }));

        try {
            const response = await fetch(`${API_V1_URL}/user-exchanges/${exchangeId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Failed to delete exchange credentials (${response.status})`);
            }

            setFormValues((prev) => ({
                ...prev,
                [exchangeKey]: getDefaultFormValues()
            }));
            setExistingData((prev) => ({
                ...prev,
                [exchangeKey]: false
            }));
            setCredentialsMetadata((prev) => ({
                ...prev,
                [exchangeKey]: {
                    hasApiKey: false,
                    hasApiSecret: false,
                    hasApiPassphrase: false
                }
            }));
            setValidationErrors((prev) => {
                if (!prev[exchangeKey]) {
                    return prev;
                }
                const next = { ...prev };
                delete next[exchangeKey];
                return next;
            });

            notify('Exchange credentials deleted successfully', { type: 'info' });
        } catch (error) {
            console.error(error);
            notify('Failed to delete exchange credentials', { type: 'error' });
        } finally {
            setDeletingState((prev) => ({ ...prev, [exchangeKey]: false }));
        }
    };

    const handleTestConnection = async (exchangeKey: string, exchangeId: string | number) => {
        setTestingState((prev) => ({ ...prev, [exchangeKey]: true }));

        try {
            const response = await fetch(`${API_V1_URL}/user-exchanges/${exchangeId}/test`, {
                method: 'POST',
                credentials: 'include'
            });

            let message = '';
            let title = 'Connection Test';

            if (response.headers.get('content-type')?.includes('application/json')) {
                const payload = await response.json();
                message = JSON.stringify(payload, null, 2);
            } else {
                message = await response.text();
            }

            if (!response.ok) {
                title = 'Connection Test Failed';
            }

            setTestModalState({
                open: true,
                title,
                message: message || 'No response returned from the server.'
            });
        } catch (error) {
            console.error(error);
            setTestModalState({
                open: true,
                title: 'Connection Test Failed',
                message: 'Unable to test the connection at this time.'
            });
        } finally {
            setTestingState((prev) => ({ ...prev, [exchangeKey]: false }));
        }
    };

    const combinedLoading = exchangesLoading || userExchangesLoading;

    if (combinedLoading) {
        return (
            <Box display="flex" justifyContent="center" mt={4}>
                <CircularProgress />
            </Box>
        );
    }

    if (!exchangeList.length) {
        return (
            <Box mt={4}>
                <Typography align="center">No exchanges available.</Typography>
            </Box>
        );
    }

    const renderTextField = (
        exchangeKey: string,
        field: FieldName,
        label: string,
        value: string,
        disabled: boolean,
        metadata: ExchangeCredentialsMetadata,
        error?: string
    ) => {
        const isVisible = fieldVisibility[exchangeKey]?.[field] ?? false;
        const hasStoredValue =
            field === 'apiKey'
                ? metadata.hasApiKey
                : field === 'apiSecret'
                ? metadata.hasApiSecret
                : metadata.hasApiPassphrase;
        const helperText = error ?? (hasStoredValue ? 'A value is already saved. Leave blank to keep the current value.' : '');

        return (
            <TextField
                label={label}
                fullWidth
                margin="normal"
                type={isVisible ? 'text' : 'password'}
                value={value}
                onChange={(event) => handleInputChange(exchangeKey, field, event.target.value)}
                autoComplete="new-password"
                disabled={disabled}
                error={Boolean(error)}
                helperText={helperText}
                placeholder={hasStoredValue ? '••••••••' : undefined}
                InputProps={{
                    endAdornment: (
                        <InputAdornment position="end">
                            <IconButton
                                edge="end"
                                onClick={() => toggleVisibility(exchangeKey, field)}
                                aria-label={`Toggle visibility for ${label}`}
                                disabled={disabled}
                            >
                                {isVisible ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                        </InputAdornment>
                    )
                }}
            />
        );
    };

    return (
        <Box
            display="grid"
            gap={2}
            gridTemplateColumns={{ xs: '1fr', md: 'repeat(2, minmax(0, 1fr))' }}
        >
            {exchangeList.map((exchange: any, index: number) => {
                const exchangeId = exchange?.id ?? exchange?.exchangeId ?? exchange?.exchange_id ?? exchange?.name ?? index;
                const exchangeKey = String(exchangeId);
                const values = formValues[exchangeKey] ?? getDefaultFormValues();
                const metadata = credentialsMetadata[exchangeKey] ?? {
                    hasApiKey: false,
                    hasApiSecret: false,
                    hasApiPassphrase: false
                };
                const hasData = existingData[exchangeKey] ?? false;
                const isSaving = savingState[exchangeKey] ?? false;
                const isDeleting = deletingState[exchangeKey] ?? false;
                const isTesting = testingState[exchangeKey] ?? false;
                const hasTestableKeys =
                    (metadata.hasApiKey || Boolean(values.apiKey?.trim())) &&
                    (metadata.hasApiSecret || Boolean(values.apiSecret?.trim()));
                const isBusy = isSaving || isDeleting;
                const errors = validationErrors[exchangeKey] ?? {};
                return (
                    <Box key={exchangeKey}>
                        <Card
                            sx={{
                                bgcolor: hasData ? 'rgba(76, 175, 80, 0.12)' : 'background.paper',
                                border: hasData ? (theme) => `1px solid ${theme.palette.success.light}` : undefined,
                                transition: 'background-color 0.3s ease, border-color 0.3s ease'
                            }}
                        >
                            <CardHeader
                                title={exchange?.name || 'Exchange'}
                                action={
                                    hasData ? (
                                        <Button
                                            variant="outlined"
                                            color="error"
                                            size="small"
                                            onClick={() => handleClear(exchangeKey, exchangeId)}
                                            disabled={isBusy}
                                        >
                                            {isDeleting ? 'Deleting…' : 'Clear data'}
                                        </Button>
                                    ) : undefined
                                }
                            />
                            <CardContent>
                                <FormControlLabel
                                    control={(
                                        <Checkbox
                                            color="primary"
                                            checked={values.runOnServer}
                                            onChange={(event) => handleCheckboxChange(exchangeKey, event.target.checked)}
                                            disabled={isBusy}
                                        />
                                    )}
                                    label="Run on server"
                                />
                                {renderTextField(
                                    exchangeKey,
                                    'apiKey',
                                    'API Key',
                                    values.apiKey,
                                    isBusy,
                                    metadata,
                                    errors.apiKey
                                )}
                                {renderTextField(
                                    exchangeKey,
                                    'apiSecret',
                                    'API Secret',
                                    values.apiSecret,
                                    isBusy,
                                    metadata,
                                    errors.apiSecret
                                )}
                                {/*{renderTextField(*/}
                                {/*    exchangeKey,*/}
                                {/*    'apiPassphrase',*/}
                                {/*    'API Passphrase',*/}
                                {/*    values.apiPassphrase,*/}
                                {/*    isBusy,*/}
                                {/*    metadata,*/}
                                {/*    errors.apiPassphrase*/}
                                {/*)}*/}
                                <Box display="flex" justifyContent="flex-end" mt={2} gap={1}>
                                    {hasTestableKeys && (
                                        <Button
                                            variant="outlined"
                                            onClick={() => handleTestConnection(exchangeKey, exchangeId)}
                                            disabled={isBusy || isTesting}
                                        >
                                            {isTesting ? 'Testing…' : 'Test connection'}
                                        </Button>
                                    )}
                                    <Button
                                        variant="contained"
                                        onClick={() => handleSave(exchangeKey, exchangeId)}
                                        disabled={isBusy}
                                    >
                                        {isSaving ? 'Saving…' : 'Save changes'}
                                    </Button>
                                </Box>
                            </CardContent>
                        </Card>
                    </Box>
                );
            })}
            <Dialog
                open={testModalState.open}
                onClose={() => setTestModalState((prev) => ({ ...prev, open: false }))}
                fullWidth
                maxWidth="sm"
            >
                <DialogTitle sx={{ pr: 6 }}>
                    {testModalState.title}
                    <IconButton
                        aria-label="Close"
                        onClick={() => setTestModalState((prev) => ({ ...prev, open: false }))}
                        sx={{ position: 'absolute', right: 8, top: 8 }}
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>
                <DialogContent dividers>
                    <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                        {testModalState.message}
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setTestModalState((prev) => ({ ...prev, open: false }))}>Close</Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default ExchangeKeysPage;
