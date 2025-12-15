// import { useInput } from 'react-admin';
// import { TextareaAutosize } from '@mui/material';
//
// export const PasteTextArea = ({ source, label }: { source: string; label: string }) => {
//     const { field } = useInput({ source });
//
//     const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
//         const items = e.clipboardData.items;
//         for (let i = 0; i < items.length; i++) {
//             if (items[i].type.indexOf('image') !== -1) {
//                 const file = items[i].getAsFile();
//                 if (file) {
//                     console.log("Imagem colada", file);
//                 }
//             }
//         }
//     };
//
//     return (
//         <div style={{ width: '100%' }}>
//             <label>{label}</label>
//             <TextareaAutosize
//                 {...field}
//                 onPaste={handlePaste}
//                 minRows={6}
//                 maxRows={20}
//                 style={{ width: '100%', fontSize: '1rem', padding: '8px' }}
//             />
//         </div>
//     );
// };

import { useState } from 'react';
import { useInput } from 'react-admin';
import {
    Box,
    TextField,
    Typography,
    IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';

const PasteTextArea = ({ source, label }: { source: string; label?: string }) => {
    const { field } = useInput({ source });
    const [imagePreviews, setImagePreviews] = useState<string[]>([]);

    const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
        const items = e.clipboardData.items;
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            if (item.type.indexOf('image') !== -1) {
                const file = item.getAsFile();
                if (file) {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64Image = reader.result as string;
                        setImagePreviews(prev => [...prev, base64Image]);

                        // Adiciona ao texto como markdown
                        field.onChange(
                            (prev: string) =>
                                (prev || '') + `\n![image](${base64Image})\n`
                        );
                    };
                    reader.readAsDataURL(file);
                }
            }
        }
    };

    const handleRemove = (index: number) => {
        const imageToRemove = imagePreviews[index];

        // Remove do preview
        const updatedPreviews = [...imagePreviews];
        updatedPreviews.splice(index, 1);
        setImagePreviews(updatedPreviews);

        // Remove do markdown
        const updatedText = (field.value || '').replace(
            `![image](${imageToRemove})\n`, ''
        );
        field.onChange(updatedText);
    };

    return (
        <Box>
            {label && (
                <Typography variant="body2" sx={{ mb: 1 }}>
                    {label}
                </Typography>
            )}

            <TextField
                {...field}
                onPaste={(e) => handlePaste(e as unknown as React.ClipboardEvent<HTMLTextAreaElement>)}
                placeholder="Write notes or paste images here..."
                multiline
                minRows={6}
                maxRows={20}
                fullWidth
                variant="outlined"
            />


            {imagePreviews.length > 0 && (
                <Box display="flex" gap={2} flexWrap="wrap" mt={2}>
                    {imagePreviews.map((src, idx) => (
                        <Box key={idx} position="relative">
                            <img
                                src={src}
                                alt={`pasted-${idx}`}
                                width={100}
                                style={{
                                    borderRadius: 4,
                                    boxShadow: '0 0 4px rgba(0,0,0,0.2)'
                                }}
                            />
                            <IconButton
                                onClick={() => handleRemove(idx)}
                                size="small"
                                sx={{
                                    position: 'absolute',
                                    top: -10,
                                    right: -10,
                                    bgcolor: 'white',
                                    boxShadow: 1
                                }}
                            >
                                <DeleteIcon fontSize="small" />
                            </IconButton>
                        </Box>
                    ))}
                </Box>
            )}
        </Box>
    );
};

export default PasteTextArea;






