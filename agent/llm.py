import json
import os
import time
import re
from typing import Generator, Optional, Dict, List
import requests
from django.conf import settings


SYSTEM_PROMPT = """
You are FinGuide, an AI-powered financial education assistant.

Your role:
- Help users understand personal finance topics such as budgeting, loans, credit, savings, retirement, and basic investing.
- Provide clear explanations, definitions, and step-by-step guidance.

Rules you must always follow:
1. Use only the provided knowledge base context when available.
   - If no relevant context is found, perform an external lookup to gather information.
   - Save any new information into the knowledge base for future use, tagging it as "External Source".
2. For any calculations (loan amortization, APR, APY, ROI, DTI, retirement growth, etc.):
   - Use the available functions/tools for math instead of estimating.
   - Present the results in simple terms and, if helpful, show the calculation steps.
3. Cite your sources every time you provide factual information, using this format:  
   (Source: Document Title, Link) or (Source: External Source)
4. Never provide personalized or direct financial advice. Instead, include the disclaimer:  
   "This information is for educational purposes only. Please consult a licensed financial advisor for decisions."
5. Maintain a professional, concise, and approachable tone.  
   - Prefer short paragraphs or bullet points.  
   - Use plain English, avoiding jargon where possible.  
   - Break down complex terms into easy-to-understand parts.  
6. Ensure reliability: if a required environment variable is missing, fall back to reading from .env or use a safe default, logging a warning.

Style guidelines:
- Organize answers clearly.  
- Use headings or bullets for multi-part explanations.  
- Always end your response with:  
  "Educational use only."
"""


class SmartFinancialAI:
    """
    Fast, intelligent financial AI that processes questions quickly and provides
    context-aware responses with immediate fallbacks.
    """
    
    def __init__(self):
        self.knowledge_patterns = self._load_knowledge_patterns()
        self.quick_responses = self._load_quick_responses()
    
    def _load_knowledge_patterns(self) -> Dict[str, List[str]]:
        """Define patterns for quick topic identification"""
        return {
            'budget': ['budget', 'budgeting', 'money management', 'spending plan', '50/30/20', 'expense tracking'],
            'debt': ['debt', 'dti', 'debt-to-income', 'debt ratio', 'credit card debt', 'loans'],
            'interest': ['compound interest', 'compounding', 'interest rate', 'apr', 'apy', 'annual percentage'],
            'savings': ['savings', 'emergency fund', 'high yield', 'save money', 'savings account'],
            'investing': ['investing', 'investment', 'stocks', 'portfolio', 'index funds', 'retirement'],
            'credit': ['credit score', 'credit report', 'credit rating', 'credit history', 'fico'],
            'mortgage': ['mortgage', 'home loan', 'house payment', 'down payment', 'refinance'],
            'insurance': ['insurance', 'life insurance', 'health insurance', 'auto insurance'],
            'taxes': ['taxes', 'tax deduction', 'ira', '401k', 'tax planning'],
            'retirement': ['retirement', 'pension', '401k', 'ira', 'roth', 'social security']
        }
    
    def _load_quick_responses(self) -> Dict[str, str]:
        """Pre-loaded expert responses for instant delivery"""
        return {
            'budget': """# Creating Your Budget 💰

## The 50/30/20 Rule aws 45 shazib
**Most popular budgeting method:**
• **50% Needs**: Rent, groceries, utilities, minimum debt payments
• **30% Wants**: Entertainment, dining out, subscriptions, hobbies
• **20% Savings**: Emergency fund, retirement, extra debt payments

## Quick Budget Setup (5 minutes)
1. **Calculate monthly income** (after taxes)
2. **List fixed expenses** (rent, insurance, loans)
3. **Track variable expenses** for 1 week
4. **Apply the 50/30/20 split**
5. **Use an app** (Mint, YNAB, or even Excel)

## Budget Categories
**Needs (50%):**
- Housing (rent/mortgage)
- Transportation (car payment, gas)
- Food (groceries)
- Utilities (electric, water, phone)
- Insurance premiums
- Minimum debt payments

**Wants (30%):**
- Entertainment & dining out
- Shopping & hobbies
- Subscriptions (Netflix, gym)
- Personal care

**Savings (20%):**
- Emergency fund (3-6 months expenses)
- Retirement (401k, IRA)
- Extra debt payments
- Goal-based savings

## Pro Tips
• **Automate savings** - pay yourself first
• **Review monthly** - adjust as needed
• **Start with $1,000 emergency fund**
• **Use the envelope method** for cash categories

*Educational use only. Consult a licensed financial advisor for personalized advice.*""",

            'debt': """# Understanding Debt-to-Income (DTI) Ratio 📊

## What is DTI?
**Simple formula:** (Total Monthly Debt ÷ Gross Monthly Income) × 100

## Example Calculation
**Monthly Income:** $5,000
**Monthly Debts:** $1,500
**DTI:** ($1,500 ÷ $5,000) × 100 = **30%**

## DTI Categories
• **Excellent**: Under 20% - Great borrowing power
• **Good**: 20-36% - Most loans approved
• **Acceptable**: 37-42% - Some loan restrictions
• **Poor**: 43%+ - Loan approval difficult

## What Counts as Debt
**✅ Include:**
- Mortgage/rent payments
- Car loans
- Credit card minimum payments
- Student loans
- Personal loans
- Child support/alimony

**❌ Don't Include:**
- Utilities, groceries, insurance
- Cell phone bills
- Subscription services

## Why DTI Matters
• **Mortgage approval** - Most lenders want <43%
• **Interest rates** - Lower DTI = better rates
• **Financial health** - Shows ability to manage debt
• **Loan amounts** - Higher DTI = smaller loans

## Improving Your DTI
**Increase Income:**
- Ask for a raise
- Start a side hustle
- Work overtime
- Get a second job

**Decrease Debt:**
- Pay extra on high-interest debt
- Consolidate loans
- Avoid new debt
- Use debt avalanche method

## Quick DTI Calculator
1. Add up all monthly debt payments
2. Divide by gross monthly income
3. Multiply by 100 for percentage

*Educational use only. Consult a licensed financial advisor for personalized advice.*""",

            'interest': """# Compound Interest: The 8th Wonder of the World 📈

## Simple Definition
**Compound interest** = Interest earning interest
You get returns on your initial money PLUS returns on previously earned returns.

## The Magic Formula
**A = P(1 + r)^t**
- A = Final amount
- P = Principal (starting amount)
- r = Annual interest rate
- t = Time in years

## Real Example: $1,000 at 7% for 30 years
**Simple Interest:** $1,000 + ($70 × 30) = $3,100
**Compound Interest:** $1,000 × (1.07)^30 = **$7,612**

**The difference:** $4,512 extra just from compounding!

## Year-by-Year Growth
- **Year 1:** $1,000 → $1,070 (earned $70)
- **Year 2:** $1,070 → $1,145 (earned $75)
- **Year 3:** $1,145 → $1,225 (earned $80)
- **Year 10:** $1,967 → $2,105 (earned $138)
- **Year 20:** $3,870 → $4,141 (earned $271)
- **Year 30:** $7,612 (total earned $6,612)

## The Rule of 72
**Quick doubling calculator:**
72 ÷ interest rate = years to double

Examples:
- 6% return: 72 ÷ 6 = 12 years to double
- 8% return: 72 ÷ 8 = 9 years to double
- 10% return: 72 ÷ 10 = 7.2 years to double

## Key Principles
1. **Time is everything** - Start early, even with $25/month
2. **Consistency beats perfection** - Regular investing wins
3. **Don't touch it** - Let compound interest work
4. **Higher rates help** - But time matters more

## Where You See Compound Interest
**Working FOR you:**
- 401(k) and IRA accounts
- Index funds and ETFs
- High-yield savings accounts
- Real estate appreciation

**Working AGAINST you:**
- Credit card debt
- Unpaid loans
- Late fees and penalties

## $100/Month Example
Starting at age 25, investing $100/month at 7% return:
- **Age 35 (10 years):** $17,309
- **Age 45 (20 years):** $52,397
- **Age 55 (30 years):** $122,709
- **Age 65 (40 years):** $262,481

**Total invested:** $48,000
**Total earned:** $214,481 from compound interest!

*Educational use only. Consult a licensed financial advisor for personalized advice.*""",

            'credit': """# Understanding Credit Scores 🏆

## What is a Credit Score?
A 3-digit number (300-850) that represents your creditworthiness.
**Higher score = Better borrowing power + Lower interest rates**

## Credit Score Ranges
• **800-850 Excellent** - Best rates, easy approval
• **740-799 Very Good** - Great rates, good terms
• **670-739 Good** - Decent rates, most loans approved
• **580-669 Fair** - Higher rates, some restrictions
• **300-579 Poor** - Difficult approval, high rates

## What Affects Your Score
**Payment History (35%)**
- On-time payments boost score
- Late payments hurt score
- Pay at least minimum, always on time

**Credit Utilization (30%)**
- How much credit you use vs. available
- Keep below 30%, ideally under 10%
- Lower is always better

**Length of Credit History (15%)**
- Longer history = better score
- Keep old accounts open
- Average age of accounts matters

**Credit Mix (10%)**
- Different types: cards, loans, mortgage
- Shows you can manage various credit

**New Credit (10%)**
- Too many new accounts hurt score
- Hard inquiries lower score temporarily
- Space out credit applications

## Quick Score Improvements
**Immediate (1-2 months):**
- Pay down credit card balances
- Pay off any past-due accounts
- Become authorized user on good account

**Short-term (3-6 months):**
- Keep credit utilization under 10%
- Pay all bills on time
- Don't close old credit cards

**Long-term (6+ months):**
- Maintain good payment history
- Let accounts age
- Gradually increase credit limits

## Free Credit Monitoring
- **Annual Credit Report:** annualcreditreport.com
- **Free Scores:** Credit Karma, Credit Sesame
- **Bank Apps:** Many banks provide free scores
- **Credit Cards:** Check your statement

## Common Credit Mistakes
❌ Closing old credit cards
❌ Maxing out credit cards
❌ Making only minimum payments
❌ Applying for multiple cards quickly
❌ Ignoring credit report errors

## Credit Score Goals
- **First-time buyers:** Aim for 620+
- **Good rates:** Target 740+
- **Best rates:** Reach 800+
- **Maintenance:** Check score monthly

*Educational use only. Consult a licensed financial advisor for personalized advice.*"""
        }
    
    def identify_topic(self, question: str) -> Optional[str]:
        """Quickly identify the main topic from a question"""
        question_lower = question.lower()
        
        # Score each topic based on keyword matches
        topic_scores = {}
        for topic, keywords in self.knowledge_patterns.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                topic_scores[topic] = score
        
        # Return the highest scoring topic
        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        return None
    
    def get_quick_response(self, question: str, context: str = "") -> str:
        """Get an instant, intelligent response"""
        # First, try to identify the topic
        topic = self.identify_topic(question)
        
        if topic and topic in self.quick_responses:
            response = self.quick_responses[topic]
            
            # If we have context from knowledge base, add it
            if context and context.strip():
                response = f"## From Knowledge Base:\n{context}\n\n---\n\n{response}"
            
            return response
        
        # If we have context but no topic match, use context
        if context and context.strip():
            return f"""# Financial Information

Based on our knowledge base:

{context}

---

**Need more specific help?** Try asking about:
• Budgeting and money management
• Debt and credit scores  
• Interest rates and loans
• Savings and investing
• Retirement planning

*Educational use only. Consult a licensed financial advisor for personalized advice.*"""
        
        # Generic helpful response with question analysis
        return self._generate_smart_fallback(question)
    
    def _generate_smart_fallback(self, question: str) -> str:
        """Generate an intelligent fallback response based on question analysis"""
        question_lower = question.lower()
        
        # Analyze question intent
        if any(word in question_lower for word in ['how', 'what', 'explain', 'define']):
            intent = "explanation"
        elif any(word in question_lower for word in ['calculate', 'formula', 'math']):
            intent = "calculation"
        elif any(word in question_lower for word in ['should', 'recommend', 'advice']):
            intent = "advice"
        else:
            intent = "general"
        
        # Generate contextual response
        if intent == "calculation":
            return f"""# Financial Calculation Help 🧮

I'd be happy to help with financial calculations! Here are some common ones I can explain:

## Popular Calculations
• **Debt-to-Income Ratio**: (Monthly debt ÷ Monthly income) × 100
• **Compound Interest**: A = P(1 + r)^t
• **Mortgage Payment**: Principal, interest, taxes, insurance
• **Emergency Fund**: 3-6 months of expenses
• **Retirement Savings**: 10-15% of income

## Your Question: "{question}"
To give you the most accurate calculation, could you provide:
- Specific numbers or amounts
- Time period involved
- Interest rates (if applicable)

*Educational use only. Consult a licensed financial advisor for personalized advice.*"""
        
        elif intent == "advice":
            return f"""# Financial Guidance 💡

I provide educational information to help you make informed decisions!

## Your Question: "{question}"

While I can't give personalized financial advice, I can explain:
• How different financial concepts work
• Common strategies people use
• What factors to consider
• Questions to ask a financial advisor

## Popular Topics
• **Budgeting**: 50/30/20 rule, expense tracking
• **Debt Management**: Payoff strategies, DTI ratios
• **Saving**: Emergency funds, high-yield accounts
• **Investing**: Index funds, 401(k), diversification
• **Credit**: Building score, managing cards

**For personalized advice**, please consult a licensed financial advisor who can review your specific situation.

*Educational use only. Consult a licensed financial advisor for personalized advice.*"""
        
        else:
            return f"""# FinGuide AI Assistant 🤖

I'm here to help you understand personal finance! 

## Your Question: "{question}"

I can provide detailed explanations on:

### 💰 **Money Management**
- Budgeting (50/30/20 rule)
- Expense tracking
- Emergency funds

### 🏦 **Banking & Credit**
- Credit scores and reports
- Debt-to-income ratios
- Loan types and terms

### 📈 **Investing & Growth**
- Compound interest
- Index funds and ETFs
- Retirement accounts (401k, IRA)

### 🏠 **Major Purchases**
- Mortgage basics
- Down payments
- Interest rates (APR vs APY)

## Try asking specific questions like:
- "How do I create a budget?"
- "What's a good credit score?"
- "How does compound interest work?"
- "What's the difference between APR and APY?"

*Educational use only. Consult a licensed financial advisor for personalized advice.*"""


# Global AI instance
_ai_instance = SmartFinancialAI()


def _openai_chat_completion(messages, temperature=0.2, max_tokens=512) -> str:
    """
    Fast AI response system with intelligent fallbacks
    """
    try:
        # Extract user question for smart processing
        user_question = ""
        context = ""
        
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if "Context:" in content and "Question:" in content:
                    parts = content.split("Question:")
                    if len(parts) > 1:
                        context_part = parts[0].replace("Context:", "").strip()
                        user_question = parts[1].strip()
                        context = context_part
                elif "Question:" in content:
                    user_question = content.split("Question:")[-1].strip()
                else:
                    user_question = content
                break
        
        # Try Hugging Face API with short timeout for speed
        url = f"{settings.HF_API_URL.rstrip('/')}/models/{settings.HF_MODEL}"
        headers = {
            'Authorization': f"Bearer {settings.HF_API_KEY}",
            'Content-Type': 'application/json',
        }
        
        # Convert messages to prompt
        prompt = ""
        for msg in messages:
            if msg.get("role") == "system":
                prompt += f"System: {msg.get('content', '')}\n\n"
            elif msg.get("role") == "user":
                prompt += f"User: {msg.get('content', '')}\n\nAssistant: "
        
        payload = {
            'inputs': prompt,
            'parameters': {
                'temperature': temperature,
                'max_new_tokens': max_tokens,
                'return_full_text': False
            }
        }
        
        # Quick API attempt with 3-second timeout
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=3)
        resp.raise_for_status()
        data = resp.json()
        
        if isinstance(data, list) and len(data) > 0:
            generated_text = data[0].get('generated_text', '')
        elif isinstance(data, dict):
            generated_text = data.get('generated_text', '')
        else:
            generated_text = str(data)
            
        if generated_text and len(generated_text.strip()) > 10:
            return generated_text
        else:
            raise Exception("Empty or invalid response from API")
            
    except Exception as e:
        print(f"[DEBUG] API failed, using smart fallback: {e}")
        # Use our intelligent AI system for instant responses
        return _ai_instance.get_quick_response(user_question, context)


def generate_response(context: str, user_message: str) -> str:
    """Fast response generation with context awareness"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": (
            f"Context:\n{context}\n\nQuestion: {user_message}\n\n"
            "Remember to cite sources and include the disclaimer."
        )},
    ]
    return _openai_chat_completion(messages)


def stream_response_text(text: str, chunk_size: int = 8) -> Generator[str, None, None]:
    """Stream text for better user experience - faster chunks"""
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i+chunk_size]) + " "
        time.sleep(0.015)  # Faster streaming