import argparse
import random
import pandas as pd
import openai
import tiktoken

import util
from agent import Agent
from secretary import Secretary
from stock import Stock
from log.custom_logger import log
from record import create_stock_record, create_trade_record, AgentRecordDaily, create_agentses_record

def get_agent(all_agents, order):
    for agent in all_agents:
        if agent.order == order:
            return agent
    return None

def handle_action(action, stock_deals, all_agents, stock, session):
    
    try:
        if action["action_type"] == "buy":
            for sell_action in stock_deals["sell"][:]:
                if action["price"] == sell_action["price"]:
                    
                    close_amount = min(action["amount"], sell_action["amount"])
                    get_agent(all_agents, action["agent"]).buy_stock(stock.name, close_amount, action["price"])
                    if not sell_action["agent"] == -1:  
                        get_agent(all_agents, sell_action["agent"]).sell_stock(stock.name, close_amount, action["price"])
                    stock.add_session_deal({"price": action["price"], "amount": close_amount})
                    create_trade_record(action["date"], session, stock.name, action["agent"], sell_action["agent"],
                                        close_amount, action["price"])

                    if action["amount"] > close_amount:  
                        log.logger.info(f"ACTION - BUY:{action['agent']}, SELL:{sell_action['agent']}, "
                                        f"STOCK:{stock.name}, PRICE:{action['price']}, AMOUNT:{close_amount}")
                        stock_deals["sell"].remove(sell_action)
                        action["amount"] -= close_amount
                    else:  
                        log.logger.info(f"ACTION - BUY:{action['agent']}, SELL:{sell_action['agent']}, "
                                        f"STOCK:{stock.name}, PRICE:{action['price']}, AMOUNT:{close_amount}")
                        sell_action["amount"] -= close_amount
                        return
            
            stock_deals["buy"].append(action)

        else:
            for buy_action in stock_deals["buy"][:]:
                if action["price"] == buy_action["price"]:
                    
                    close_amount = min(action["amount"], buy_action["amount"])
                    get_agent(all_agents, action["agent"]).sell_stock(stock.name, close_amount, action["price"])
                    get_agent(all_agents, buy_action["agent"]).buy_stock(stock.name, close_amount, action["price"])
                    stock.add_session_deal({"price": action["price"], "amount": close_amount})
                    create_trade_record(action["date"], session, stock.name, buy_action["agent"], action["agent"],
                                        close_amount, action["price"])

                    if action["amount"] > close_amount:  
                        log.logger.info(f"ACTION - BUY:{buy_action['agent']}, SELL:{action['agent']}, "
                                        f"STOCK:{stock.name}, PRICE:{action['price']}, AMOUNT:{close_amount}")
                        stock_deals["buy"].remove(buy_action)
                        action["amount"] -= close_amount
                    else:  
                        log.logger.info(f"ACTION - BUY:{buy_action['agent']}, SELL:{action['agent']}, "
                                        f"STOCK:{stock.name}, PRICE:{action['price']}, AMOUNT:{close_amount}")
                        buy_action["amount"] -= close_amount
                        return
            stock_deals["sell"].append(action)
    except Exception as e:
        log.logger.error(f"handle_action error: {e}")
        return


def simulation(args):
    
    secretary = Secretary(args.model)
    stock_a = Stock("A", util.STOCK_A_INITIAL_PRICE, 0, is_new=False)
    
    stock_b = Stock("B", util.STOCK_B_INITIAL_PRICE, 0, is_new=False)
    all_agents = []
    log.logger.debug("Agents initial...")
    for i in range(0, util.AGENTS_NUM):  
        agent = Agent(i, stock_a.get_price(), stock_b.get_price(), secretary, args.model)
        all_agents.append(agent)
        log.logger.debug("cash: {}, stock a: {}, stock b:{}, debt: {}".format(agent.cash, agent.stock_a_amount,
                                                                              agent.stock_b_amount, agent.loans))

    
    last_day_forum_message = []
    stock_a_deals = {"sell": [], "buy": []}
    stock_b_deals = {"sell": [], "buy": []}
    
    

    log.logger.debug("--------Simulation Start!--------")
    for date in range(1, util.TOTAL_DATE + 1):

        log.logger.debug(f"--------DAY {date}---------")
        
        stock_a_deals["sell"].clear()
        stock_a_deals["buy"].clear()
        stock_b_deals["buy"].clear()

        
        stock_b_deals["sell"].clear()
        
        
        
        
        

        
        for agent in all_agents[:]:
            agent.chat_history.clear()  
            agent.loan_repayment(date)

        
        if date in util.REPAYMENT_DAYS:
            for agent in all_agents[:]:
                agent.interest_payment()

        
        for agent in all_agents[:]:
            if agent.is_bankrupt:
                quit_sig = agent.bankrupt_process(stock_a.get_price(), stock_b.get_price())
                if quit_sig:
                    agent.quit = True
                    all_agents.remove(agent)

        
        if date == util.EVENT_1_DAY:
            util.LOAN_RATE = util.EVENT_1_LOAN_RATE
            last_day_forum_message.append({"name": -1, "message": util.EVENT_1_MESSAGE})
        if date == util.EVENT_2_DAY:
            util.LOAN_RATE = util.EVENT_2_LOAN_RATE
            last_day_forum_message.append({"name": -1, "message": util.EVENT_2_MESSAGE})

        
        daily_agent_records = []
        for agent in all_agents:
            loan = agent.plan_loan(date, stock_a.get_price(), stock_b.get_price(), last_day_forum_message)
            daily_agent_records.append(AgentRecordDaily(date, agent.order, loan))

        for session in range(1, util.TOTAL_SESSION + 1):
            log.logger.debug(f"SESSION {session}")
            
            sequence = list(range(len(all_agents)))
            random.shuffle(sequence)
            for i in sequence:
                agent = all_agents[i]
                
                

                action = agent.plan_stock(date, session, stock_a, stock_b, stock_a_deals, stock_b_deals)
                proper, cash, valua_a, value_b = agent.get_proper_cash_value(stock_a.get_price(), stock_b.get_price())
                create_agentses_record(agent.order, date, session, proper, cash, valua_a, value_b, action)
                action["agent"] = agent.order
                action["date"] = date
                if not action["action_type"] == "no":
                    if action["stock"] == 'A':
                        handle_action(action, stock_a_deals, all_agents, stock_a, session)
                    else:
                        handle_action(action, stock_b_deals, all_agents, stock_b, session)

            
            stock_a.update_price(date)
            stock_b.update_price(date)
            create_stock_record(date, session, stock_a.get_price(), stock_b.get_price())


        
        for idx, agent in enumerate(all_agents):
            estimation = agent.next_day_estimate()
            log.logger.info("Agent {} tomorrow estimation: {}".format(agent.order, estimation))
            if idx >= len(daily_agent_records):
                break
            daily_agent_records[idx].add_estimate(estimation)
            daily_agent_records[idx].write_to_excel()
        daily_agent_records.clear()

        
        last_day_forum_message.clear()
        log.logger.debug(f"DAY {date} ends, display forum messages...")
        for agent in all_agents:
            chat_history = agent.chat_history
            message = agent.post_message()
            log.logger.info("Agent {} says: {}".format(agent.order, message))
            last_day_forum_message.append({"name": agent.order, "message": message})



    log.logger.debug("--------Simulation finished!--------")
    log.logger.debug("--------Agents action history--------")
    
    
    
    
    
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="gemini-pro", help="model name")
    args = parser.parse_args()
    simulation(args)
