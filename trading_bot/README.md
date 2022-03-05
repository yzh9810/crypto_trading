# Johnny the Trading Bot
> Would you rather live in peace as Mr. Nobody, or go down for all times in a blaze of glory?

## Production Memo
Remember to set up .env vars in case of production mode, switch to the correct branch, and...
> Time to party like it's 2023

## Strategy Expansion
Adding new strategy needs these registrations:

1. strategyRegistrarMapping in Factory.index;

2. new Enum registered in Strategy Enum

3. new commodore initialization registered in unique order logic factory

4. Its unique strategy folder containing Strategy of major coins & index for its Commodore

## Order Logic Expansion

Adding new order logic needs these registrations:

1. unique order logic factory registered in Factory.index

2. Enum registration in TradingTypeEnum

3. ALL OF THE ABOVE FOR NEW STRAT

## Routine

1. Regularly use Scripts to update datasets to achieve fast initialization

2. Regularly check logs and errorlog.txt

## Server Tips
nohup python main.py >> errorlog.txt &

ps aux | grep python

kill -9 *__PID__*