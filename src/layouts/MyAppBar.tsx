import {
    AppBarProps,
    UserMenu,
    Logout,
    MenuItemLink,
    useGetIdentity,
    RefreshIconButton,
    ToggleThemeButton
} from 'react-admin';
import { AppBar as MuiAppBar, Toolbar, Typography, Box } from '@mui/material';
import { AccountCircle } from '@mui/icons-material';
import SettingsIcon from '@mui/icons-material/Settings';
import { Link } from 'react-router-dom';
import React from 'react';
import { PageMenu } from '../components/PageMenu';

const MyUserMenu = (props: any) => (
    <UserMenu {...props}>
        <MenuItemLink
            to="/profile"
            primaryText="Profile"
            leftIcon={<AccountCircle />}
            component={Link}
        />
        <MenuItemLink
            to="/exchange-keys"
            primaryText="Exchange Keys"
            leftIcon={<SettingsIcon />}
            component={Link}
        />
        <Logout />
    </UserMenu>
);

// 🛠 FIX: wrap MuiAppBar in React.forwardRef + cast props to any to avoid overload TS error
const MyAppBar = React.forwardRef((props: AppBarProps, ref) => {
    const { data: identity } = useGetIdentity();

    return (
        <MuiAppBar
            position="sticky"
            color="primary"
            elevation={1}
            ref={ref}
            {...(props as any)} // 👈 bypass TS sx typing incompatibility
        >
            <Toolbar sx={{ position: 'relative', minHeight: 64 }}>
                <PageMenu />

                <Typography
                    variant="h6"
                    color="inherit"
                    sx={{
                        position: 'absolute',
                        left: '50%',
                        transform: 'translateX(-50%)',
                    }}
                >
                    Trading Journal
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', marginLeft: 'auto' }}>
                    <RefreshIconButton />
                    <ToggleThemeButton />
                    <Typography color="inherit" sx={{ ml: 1 }}>
                        {identity?.fullName}
                    </Typography>
                    {props.userMenu}
                </Box>
            </Toolbar>
        </MuiAppBar>
    );
});

export default (props: any) => <MyAppBar userMenu={<MyUserMenu />} {...props} />;
