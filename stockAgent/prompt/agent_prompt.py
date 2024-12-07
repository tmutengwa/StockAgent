from procoder.prompt import *









BACKGROUND_PROMPT = NamedBlock(
    name="Background",
    content=
)










LASTDAY_FORUM_AND_STOCK_PROMPT = NamedBlock(
    name="Last Day Forum and Stock",
    content=
)











LOAN_TYPE_PROMPT = NamedVariable(
    refname="loan_type_prompt",
    name="Loan Type",
    content=
)















DECIDE_IF_LOAN_PROMPT = NamedBlock(
    name="Instruction",
    content=
)












LOAN_RETRY_PROMPT = NamedBlock(
    name="Instruction",
    content=
)















DECIDE_BUY_STOCK_PROMPT = NamedBlock(
    name="Instruction",
    content=
)












BUY_STOCK_RETRY_PROMPT = NamedBlock(
    name="Instruction",
    content=
)









FIRST_DAY_FINANCIAL_REPORT = NamedVariable(
    refname="first_day_financial_prompt",
    name="The last 3 years financial report of Stock A and B",
    content=
)

FIRST_DAY_BACKGROUND_KNOWLEDGE = NamedBlock(
    name="The initial financial situation of Stock A and B",
    content=
)










SEASONAL_FINANCIAL_REPORT = NamedVariable(
    refname="seasonal_financial_report",
    name="The Seasonal financial report of Stock A and B",
    content=
)








POST_MESSAGE_PROMPT = NamedBlock(
    refname="post_message",
    name="Instruction",
    content=
)











NEXT_DAY_ESTIMATE_PROMPT = NamedBlock(
    refname="next_day_estimate",
    name="Instruction",
    content=
)











NEXT_DAY_ESTIMATE_RETRY = NamedBlock(
    refname="next_day_estimate_retry",
    name="Instruction",
    content=
)