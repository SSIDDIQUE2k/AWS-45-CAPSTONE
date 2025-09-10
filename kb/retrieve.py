from typing import List, Tuple
from django.db.models import F
from django.conf import settings
from pgvector.django import L2Distance

from .models import Chunk, Document


def load_embedder():
    try:
        from sentence_transformers import SentenceTransformer  # local import to avoid OMP init at startup
    except Exception:
        return None
    try:
        return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    except Exception:
        return None


def vector_search(query: str, k: int = 5) -> List[Tuple[Chunk, float]]:
    embedder = load_embedder()
    if not embedder:
        # Fallback: naive keyword search
        qs = Chunk.objects.filter(text__icontains=query)[:k]
        return [(c, 0.0) for c in qs]
    try:
        qvec = embedder.encode([query])[0].tolist()
        qs = (
            Chunk.objects.exclude(embedding=None)
            .annotate(distance=L2Distance(F('embedding'), qvec))
            .order_by('distance')[:k]
        )
        return [(c, float(getattr(c, 'distance', 0.0))) for c in qs]
    except Exception:
        qs = Chunk.objects.filter(text__icontains=query)[:k]
        return [(c, 0.0) for c in qs]


def external_lookup(query: str) -> str:
    """
    Enhanced external lookup that provides comprehensive financial education content
    based on the query. This simulates pulling from authoritative financial sources.
    """
    query_lower = query.lower()
    
    # Budget-related queries
    if any(word in query_lower for word in ["budget", "budgeting", "money management"]):
        return """# Creating and Managing a Budget

A budget is a plan for how you'll spend your money over a specific period. The most popular budgeting method is the 50/30/20 rule:

## The 50/30/20 Rule
- **50% for Needs**: Essential expenses like rent, groceries, utilities, insurance, minimum debt payments
- **30% for Wants**: Entertainment, dining out, hobbies, subscriptions, non-essential shopping
- **20% for Savings & Debt**: Emergency fund, retirement savings, extra debt payments, investments

## Steps to Create Your Budget
1. **Calculate Monthly Income**: Add up all income sources after taxes
2. **Track Current Expenses**: Monitor spending for 2-4 weeks to understand patterns
3. **Categorize Expenses**: Sort into needs, wants, and savings
4. **Set Spending Limits**: Assign dollar amounts to each category
5. **Monitor & Adjust**: Review monthly and make necessary changes

## Budgeting Methods
- **Zero-Based Budgeting**: Every dollar is assigned a purpose
- **Envelope Method**: Use cash for different spending categories
- **Pay Yourself First**: Save before spending on wants

## Helpful Tools
- Apps: Mint, YNAB (You Need A Budget), EveryDollar
- Spreadsheets: Simple category tracking
- Bank apps: Many offer built-in budgeting features

Source: Financial Planning Association, National Endowment for Financial Education"""

    # Debt-to-income ratio queries
    elif any(word in query_lower for word in ["debt to income", "debt-to-income", "dti", "debt ratio"]):
        return """# Understanding Debt-to-Income Ratio (DTI)

Debt-to-Income ratio is a key financial metric that compares your total monthly debt payments to your gross monthly income.

## DTI Formula
DTI = (Total Monthly Debt Payments ÷ Gross Monthly Income) × 100

## What Counts as Debt
**Included:**
- Mortgage or rent payments
- Car loan payments
- Credit card minimum payments
- Student loan payments
- Personal loan payments
- Other loan payments

**Not Included:**
- Utilities (unless in collections)
- Insurance premiums
- Groceries and everyday expenses
- Income taxes

## DTI Categories
- **Excellent**: Below 20% - Very low financial risk
- **Good**: 20-36% - Manageable debt load
- **Acceptable**: 37-42% - Higher but still manageable
- **High Risk**: Above 43% - May struggle with additional debt

## Why DTI Matters
- Lenders use it to assess loan approval risk
- Higher DTI can mean higher interest rates
- Helps you understand your financial health
- Guides decisions about taking on new debt

## Improving Your DTI
- Increase income through raises, side jobs, or better employment
- Pay down existing debt faster
- Avoid taking on new debt
- Consider debt consolidation at lower rates

Source: Consumer Financial Protection Bureau, Federal Housing Administration"""

    # Compound interest queries  
    elif any(word in query_lower for word in ["compound interest", "compounding", "interest growth"]):
        return """# Understanding Compound Interest

Compound interest is the interest you earn on both your original money and on previously earned interest. Albert Einstein allegedly called it "the eighth wonder of the world."

## How It Works
Unlike simple interest (only on principal), compound interest grows exponentially:
- Year 1: $1,000 × 7% = $1,070
- Year 2: $1,070 × 7% = $1,145 (earned $75 on the $70 from year 1)
- Year 3: $1,145 × 7% = $1,225 (compound effect accelerates)

## The Formula
A = P(1 + r/n)^(nt)
- A = Final amount
- P = Principal (starting amount)
- r = Annual interest rate (as decimal)
- n = Number of times compounded per year
- t = Number of years

## Example Calculation
$1,000 invested at 7% annually for 30 years:
- Simple Interest: $1,000 + ($1,000 × 0.07 × 30) = $3,100
- Compound Interest: $1,000 × (1.07)^30 = $7,612

## The Rule of 72
Estimate doubling time: 72 ÷ interest rate = years to double
- At 6%: 72 ÷ 6 = 12 years to double
- At 9%: 72 ÷ 9 = 8 years to double

## Key Principles
1. **Time is crucial**: Start early, even with small amounts
2. **Consistency matters**: Regular contributions amplify growth
3. **Rate helps**: But time is often more important than rate
4. **Frequency matters**: More frequent compounding = more growth

## Real-World Applications
- Retirement accounts (401k, IRA)
- High-yield savings accounts
- Investment accounts
- Education savings (529 plans)
- **Debt works against you**: Credit cards compound debt

Source: Securities and Exchange Commission, Financial Industry Regulatory Authority"""

    # APR vs APY queries
    elif any(word in query_lower for word in ["apr", "apy", "annual percentage", "interest rate"]):
        return """# APR vs APY: Understanding the Difference

These two terms are often confused but measure completely different things in your financial life.

## APR (Annual Percentage Rate)
- **What you PAY** on loans and credit cards
- Includes the interest rate PLUS fees
- Shows the true cost of borrowing money
- Higher APR = more expensive loan

### APR Includes:
- Base interest rate
- Origination fees
- Processing fees
- Discount points (for mortgages)
- Other loan-related costs

## APY (Annual Percentage Yield)  
- **What you EARN** on savings and investments
- Accounts for compound interest effects
- Shows total return on your money
- Higher APY = better return

### APY Factors:
- Interest rate
- Compounding frequency (daily, monthly, quarterly)
- Time period

## Key Differences

| Aspect | APR | APY |
|--------|-----|-----|
| Purpose | Cost of borrowing | Return on savings |
| Best when | Lower | Higher |
| Includes fees | Yes | No |
| Compound effect | No | Yes |

## Examples

**Loan (APR):**
- $10,000 car loan at 5.5% APR
- True cost including fees

**Savings (APY):**
- $10,000 in savings at 4.5% APY
- Actual annual return with compounding

## Shopping Tips
- **For loans**: Compare APRs (lower is better)
- **For savings**: Compare APYs (higher is better)
- Don't compare APR to APY directly
- Read the fine print for fees and terms

Source: Federal Trade Commission, National Credit Union Administration"""

    # Emergency fund queries
    elif any(word in query_lower for word in ["emergency fund", "emergency savings", "financial safety"]):
        return """# Building an Emergency Fund

An emergency fund is money set aside to cover unexpected expenses or financial emergencies without going into debt.

## Why You Need One
- Job loss or reduced income
- Medical emergencies
- Major car repairs
- Home repairs (HVAC, plumbing, roof)
- Family emergencies
- Prevents debt accumulation during crises

## How Much to Save
**Beginner Goal**: $1,000 minimum
**Standard Goal**: 3-6 months of living expenses
**Higher Security**: 6-12 months for irregular income

### Calculating Your Target
1. List monthly essential expenses:
   - Rent/mortgage
   - Utilities
   - Groceries
   - Insurance
   - Minimum debt payments
   - Transportation
2. Multiply by 3-6 months

## Where to Keep Emergency Funds
**Best Options:**
- High-yield savings account
- Money market account
- Short-term CDs (certificates of deposit)

**Avoid:**
- Checking accounts (too easy to spend)
- Investment accounts (too risky)
- Retirement accounts (penalties)

## Building Your Fund
1. **Start small**: Even $25/month helps
2. **Automate transfers**: Set up automatic savings
3. **Use windfalls**: Tax refunds, bonuses, gifts
4. **Side income**: Temporarily increase earnings
5. **Cut expenses**: Redirect savings to emergency fund

## When to Use It
**YES:**
- Job loss
- Medical bills
- Essential home/car repairs
- Family emergencies

**NO:**
- Vacations
- Shopping sales
- Non-essential purchases
- Paying off low-interest debt

Source: National Endowment for Financial Education, Certified Financial Planner Board"""

    # Credit score queries
    elif any(word in query_lower for word in ["credit score", "credit report", "credit rating"]):
        return """# Understanding Credit Scores

A credit score is a three-digit number (typically 300-850) that represents your creditworthiness based on your credit history.

## Credit Score Ranges (FICO)
- **Exceptional**: 800-850
- **Very Good**: 740-799  
- **Good**: 670-739
- **Fair**: 580-669
- **Poor**: 300-579

## What Affects Your Credit Score

### Payment History (35%)
- Most important factor
- Pay all bills on time
- Late payments hurt your score
- Defaults and bankruptcies have major impact

### Credit Utilization (30%)
- Percentage of available credit you use
- Keep below 30%, ideally under 10%
- Example: $1,000 limit, use less than $300

### Length of Credit History (15%)
- How long you've had credit accounts
- Keep old accounts open
- Average age of accounts matters

### Credit Mix (10%)
- Different types of credit
- Credit cards, car loans, mortgages
- Shows you can manage various credit types

### New Credit (10%)
- Recent credit inquiries
- New accounts opened
- Too many inquiries lower score temporarily

## Improving Your Credit Score
1. **Pay bills on time** - most important
2. **Keep credit utilization low** - below 30%
3. **Don't close old credit cards**
4. **Pay down existing debt**
5. **Limit new credit applications**
6. **Monitor credit reports** for errors
7. **Consider becoming authorized user** on family member's account

## Checking Your Credit
- **Free annual reports**: annualcreditreport.com
- **Free monitoring**: Credit Karma, banks, credit card companies
- **Full FICO scores**: myFICO.com (paid)

## Credit vs Debit
- **Credit cards**: Build credit history, fraud protection
- **Debit cards**: Spend your own money, no credit building

Source: Fair Isaac Corporation (FICO), Consumer Financial Protection Bureau"""

    # Default response for other financial topics
    else:
        return f"""# Financial Education: {query}

This appears to be a financial question about: {query}

For comprehensive financial education on topics like budgeting, debt management, investing, credit scores, and financial planning, I recommend consulting these authoritative sources:

## Reliable Financial Education Sources:
- **Consumer Financial Protection Bureau (CFPB)**: consumerfinance.gov
- **National Endowment for Financial Education**: nefe.org  
- **Financial Planning Association**: plannersearch.org
- **Securities and Exchange Commission**: investor.gov
- **Federal Trade Commission**: consumer.ftc.gov
- **IRS Tax Information**: irs.gov

## Common Financial Topics:
- Emergency fund planning
- Debt-to-income ratios
- Credit score improvement
- Investment basics
- Retirement planning
- Insurance needs
- Tax planning strategies

For personalized financial advice, please consult with a licensed financial advisor, accountant, or financial planner.

Source: Multiple authoritative financial education organizations"""


def retrieve_with_fallback(query: str, top_k: int = 5) -> Tuple[str, List[Document]]:
    results = vector_search(query, k=top_k)
    if not results:
        # Self-learning: perform external lookup and ingest
        text = external_lookup(query)
        doc = Document.objects.create(title=f"External: {query}", source='external')
        Chunk.objects.create(document=doc, text=text, order=0, embedding=None)
        ctx = text
        docs = [doc]
    else:
        chunks = [c for c, _ in results]
        docs = list({c.document for c in chunks})
        ctx = "\n\n".join(c.text for c in chunks)
    return ctx, docs
