export type TradeType = 'spot' | 'futures';

export interface Trade {
    id: number;
    symbol: string;
    type: TradeType;
    leverage?: number;
    entry_price: number;
    exit_price: number;
    fee?: number;
    indicators?: string;
    sentiment?: string;
    stop_loss?: number;
    take_profit?: number;
    exchange?: string;
    date: string;
}
