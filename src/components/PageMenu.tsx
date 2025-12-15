import React, { useState } from 'react';
import { MenuItemLink } from 'react-admin';
import { Menu as MuiMenu, IconButton } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ListIcon from '@mui/icons-material/List';
import HttpIcon from '@mui/icons-material/Http';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import SearchIcon from '@mui/icons-material/Search';

export const PageMenu = () => {
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);

    const handleOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    return (
        <>
            <IconButton
                color="inherit"
                onClick={handleOpen}
                size="large"
                edge="start"
                sx={{ mr: 2 }}
            >
                <MenuIcon />
            </IconButton>
            <MuiMenu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
            >
                <MenuItemLink
                    to="/"
                    primaryText="Dashboard"
                    onClick={handleClose}
                    leftIcon={<DashboardIcon fontSize="small" />}
                />
                {/*<MenuItemLink*/}
                {/*    to="/trades"*/}
                {/*    primaryText="Trades"*/}
                {/*    onClick={handleClose}*/}
                {/*    leftIcon={<ListIcon fontSize="small" />}*/}
                {/*/>*/}
                <MenuItemLink
                    to="/orders"
                    primaryText="Orders"
                    onClick={handleClose}
                    leftIcon={<SearchIcon fontSize="small" />}
                />
                <MenuItemLink
                    to="/webhooks"
                    primaryText="Webhooks"
                    onClick={handleClose}
                    leftIcon={<HttpIcon fontSize="small" />}
                />
                <MenuItemLink
                    to="/webhook-alerts"
                    primaryText="Alerts"
                    onClick={handleClose}
                    leftIcon={<NotificationsActiveIcon fontSize="small" />}
                />
            </MuiMenu>
        </>
    );
};
