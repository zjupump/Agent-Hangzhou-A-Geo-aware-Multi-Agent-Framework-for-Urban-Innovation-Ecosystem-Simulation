from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..agents.base_agent import BaseAgent


@dataclass
class JobPosting:
    employer_uid: str
    role: str
    salary: float
    rent_support: float = 0.0
    location: Optional[Tuple[float, float]] = None
    requirements: Dict[str, Any] = field(default_factory=dict)
    filled: bool = False
    candidate_uid: Optional[str] = None


@dataclass
class Company:
    uid: str
    founders: List[str]
    employees: List[str] = field(default_factory=list)
    capital: float = 0.0
    revenue: float = 0.0
    operating_cost_rate: float = 0.1
    rent_expense: float = 0.0
    status: str = "active"
    stage: str = "seed"
    history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class InvestmentRound:
    company_uid: str
    round_type: str
    target_amount: float
    raised_amount: float = 0.0
    investors: List[str] = field(default_factory=list)


class Economy:
    def __init__(
        self,
        wage_rate: float = 1.0,
        rent_rate: float = 1.0,
        cost_multiplier: float = 1.0,
    ):
        self.job_postings: List[JobPosting] = []
        self.companies: Dict[str, Company] = {}
        self.investment_rounds: List[InvestmentRound] = []
        self.wage_rate = wage_rate
        self.rent_rate = rent_rate
        self.cost_multiplier = cost_multiplier

    def post_job(
        self,
        employer: BaseAgent,
        role: str,
        salary: float,
        rent_support: float = 0.0,
        location: Optional[Tuple[float, float]] = None,
        requirements: Optional[Dict[str, Any]] = None,
    ) -> JobPosting:
        posting = JobPosting(
            employer_uid=employer.uid,
            role=role,
            salary=salary,
            rent_support=rent_support,
            location=location,
            requirements=requirements or {},
        )
        self.job_postings.append(posting)
        return posting

    def search_jobs(
        self,
        agent: BaseAgent,
        role_preferences: Optional[List[str]] = None,
    ) -> List[JobPosting]:
        preferred = role_preferences or [agent.role]
        available = []
        for posting in self.job_postings:
            if posting.filled:
                continue
            if posting.role in preferred:
                meets_requirements = all(
                    agent.attributes.get(k) >= v for k, v in posting.requirements.items()
                )
                if meets_requirements:
                    available.append(posting)
        return available

    def hire(
        self,
        candidate: BaseAgent,
        posting: JobPosting,
        environment: Optional[Any] = None,
    ) -> bool:
        if posting.filled:
            return False
        posting.filled = True
        posting.candidate_uid = candidate.uid
        candidate.state["employer"] = posting.employer_uid
        candidate.state["salary"] = posting.salary
        candidate.state["rent_support"] = posting.rent_support
        if environment and hasattr(environment, "register_employment"):
            environment.register_employment(candidate, posting)
        return True

    def pay_wages(self, company: Company, environment: Optional[Any] = None) -> float:
        payroll = 0.0
        for employee_uid in company.employees:
            if environment and hasattr(environment, "get_agent_by_uid"):
                employee = environment.get_agent_by_uid(employee_uid)
                if employee:
                    salary = employee.state.get("salary", 0.0)
                    payroll += salary
        company.capital -= payroll
        if environment and hasattr(environment, "record_payroll"):
            environment.record_payroll(company, payroll)
        return payroll

    def apply_rent_costs(
        self,
        agent: BaseAgent,
        location_quality: float = 1.0,
        environment: Optional[Any] = None,
    ) -> float:
        rent = agent.state.get("rent_support", 0.0) + self.rent_rate * location_quality
        agent.state["rent"] = rent
        if environment and hasattr(environment, "record_rent"):
            environment.record_rent(agent, rent)
        return rent

    def calculate_operating_costs(
        self,
        company: Company,
        environment: Optional[Any] = None,
    ) -> float:
        cost = company.revenue * company.operating_cost_rate * self.cost_multiplier
        company.capital -= cost
        company.history.append({"step": environment.current_step if environment else None, "costs": cost})
        return cost

    def create_company(
        self,
        entrepreneur: BaseAgent,
        team: List[BaseAgent],
        initial_capital: float,
        environment: Optional[Any] = None,
    ) -> Company:
        company = Company(
            uid=f"company_{entrepreneur.uid}",
            founders=[entrepreneur.uid] + [member.uid for member in team if member.uid != entrepreneur.uid],
            capital=initial_capital,
            stage="seed",
        )
        self.companies[company.uid] = company
        if environment and hasattr(environment, "register_company"):
            environment.register_company(company)
        return company

    def grow_company(
        self,
        company: Company,
        investment: float,
        revenue_increment: float = 0.0,
        environment: Optional[Any] = None,
    ) -> None:
        company.capital += investment
        company.revenue += revenue_increment
        if company.revenue > company.capital * 0.5:
            company.stage = "growth"
        if environment and hasattr(environment, "record_growth"):
            environment.record_growth(company, investment, revenue_increment)

    def evaluate_failure(
        self,
        company: Company,
        threshold: float = 0.0,
        environment: Optional[Any] = None,
    ) -> bool:
        if company.capital < threshold or company.revenue < 0:
            company.status = "failed"
            if environment and hasattr(environment, "deregister_company"):
                environment.deregister_company(company)
            return True
        return False

    def match_investor(
        self,
        entrepreneur: BaseAgent,
        investors: List[BaseAgent],
        required_amount: float,
        round_type: str = "seed",
        environment: Optional[Any] = None,
    ) -> Optional[InvestmentRound]:
        available = [inv for inv in investors if inv.state.get("capital", 0.0) >= required_amount * 0.2]
        if not available:
            return None
        investor = available[0]
        amount = min(required_amount, investor.state["capital"] * 0.5)
        investor.state["capital"] -= amount
        round_record = InvestmentRound(
            company_uid=f"company_{entrepreneur.uid}",
            round_type=round_type,
            target_amount=required_amount,
            raised_amount=amount,
            investors=[investor.uid],
        )
        self.investment_rounds.append(round_record)
        if environment and hasattr(environment, "record_investment"):
            environment.record_investment(entrepreneur, investor, amount, round_type)
        return round_record

    def financing_round(
        self,
        company: Company,
        investors: List[BaseAgent],
        target_amount: float,
        round_type: str = "series_a",
        environment: Optional[Any] = None,
    ) -> float:
        raised = 0.0
        for investor in investors:
            available = investor.state.get("capital", 0.0) * 0.3
            contribution = min(target_amount - raised, available)
            investor.state["capital"] -= contribution
            raised += contribution
            if environment and hasattr(environment, "record_investment_round"):
                environment.record_investment_round(company, investor, contribution, round_type)
            if raised >= target_amount:
                break
        company.capital += raised
        company.stage = "scale" if raised >= target_amount else company.stage
        return raised

    def settle_transaction(
        self,
        buyer: BaseAgent,
        seller: BaseAgent,
        amount: float,
        goods: Optional[str] = None,
        environment: Optional[Any] = None,
    ) -> bool:
        buyer.state["wealth"] = buyer.state.get("wealth", 0.0) - amount
        seller.state["wealth"] = seller.state.get("wealth", 0.0) + amount
        if environment and hasattr(environment, "record_transaction"):
            environment.record_transaction(buyer, seller, amount, goods)
        return True

    def resolve_market_conflict(
        self,
        party_a: BaseAgent,
        party_b: BaseAgent,
        issue: str,
        environment: Optional[Any] = None,
    ) -> Dict[str, Any]:
        settlement = {
            "party_a": party_a.uid,
            "party_b": party_b.uid,
            "issue": issue,
            "resolved": True,
        }
        if environment and hasattr(environment, "log_market_conflict"):
            environment.log_market_conflict(party_a, party_b, issue)
        return settlement

    def enforce_wage_rent_constraints(
        self,
        agent: BaseAgent,
        environment: Optional[Any] = None,
    ) -> None:
        salary = agent.state.get("salary", 0.0)
        rent = agent.state.get("rent", 0.0)
        budget = agent.state.get("wealth", 0.0)
        if salary + rent > budget:
            agent.state["stress"] = (salary + rent) - budget
        else:
            agent.state["stress"] = 0.0
        if environment and hasattr(environment, "record_agent_financials"):
            environment.record_agent_financials(agent)
