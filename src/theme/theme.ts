// import { createTheme } from '@mui/material/styles';
//
// export const theme = createTheme({
//     palette: {
//         primary: {
//             main: '#006a4e', // 🌿 Dark emerald green
//         },
//     },
// });
//
// export const lightTheme = createTheme({
//     palette: {
//         mode: 'light',
//         primary: {
//             main: '#006a4e', // emerald green
//         },
//     },
// });
//
// export const darkTheme = createTheme({
//     palette: {
//         mode: 'dark',
//         primary: {
//             main: '#004d39', // deeper emerald for dark background
//         },
//     },
// });
//
import { createTheme } from '@mui/material/styles';
import { RaThemeOptions } from 'react-admin';

export const lightTheme: RaThemeOptions = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#006a4e',
        },
    },
    shape: {
        borderRadius: 4, // force number
    },
}) as RaThemeOptions;

export const darkTheme: RaThemeOptions = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#004d39',
        },
    },
    shape: {
        borderRadius: 4,
    },
}) as RaThemeOptions;
