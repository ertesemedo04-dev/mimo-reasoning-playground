"""Pre-built reasoning challenges for exploring MiMo's capabilities."""

from dataclasses import dataclass


@dataclass
class Challenge:
    """A reasoning challenge with prompt and metadata."""
    id: str
    title: str
    category: str
    difficulty: str  # easy, medium, hard, extreme
    prompt: str
    system: str = ""
    description: str = ""


CHALLENGES = [
    # ── Logic & Math ──
    Challenge(
        id="logic-001",
        title="The Missing Dollar",
        category="Logic",
        difficulty="medium",
        description="Classic puzzle that trips up reasoning models.",
        prompt=(
            "Three friends split a hotel bill. The receptionist charges them $30, "
            "so each pays $10. Later, the receptionist realizes the bill should be $25 "
            "and gives the bellboy $5 to return. The bellboy keeps $2 and gives $1 back "
            "to each friend. Now each friend paid $9 (total $27), the bellboy has $2. "
            "That's $29. Where is the missing dollar?"
        ),
    ),
    Challenge(
        id="logic-002",
        title="Monty Hall Problem",
        category="Logic",
        difficulty="medium",
        description="Probability reasoning with the classic Monty Hall scenario.",
        prompt=(
            "You're on a game show. There are 3 doors. Behind one is a car, behind "
            "the others are goats. You pick door 1. The host, who knows what's behind "
            "each door, opens door 3 to reveal a goat. Should you switch to door 2? "
            "Explain your reasoning step by step with probability calculations."
        ),
    ),
    Challenge(
        id="math-001",
        title="Infinite Series",
        category="Math",
        difficulty="hard",
        description="Evaluate a convergent infinite series.",
        prompt=(
            "Evaluate the infinite series: S = 1/1·2 + 1/2·3 + 1/3·4 + ... + 1/n·(n+1) + ...\n\n"
            "Show your complete reasoning, including partial fraction decomposition "
            "and the telescoping pattern."
        ),
    ),
    Challenge(
        id="math-002",
        title="Combinatorial Proof",
        category="Math",
        difficulty="hard",
        description="Prove an identity using combinatorial arguments.",
        prompt=(
            "Prove that C(n,0) + C(n,1) + C(n,2) + ... + C(n,n) = 2^n\n\n"
            "Provide TWO different proofs:\n"
            "1. Using the binomial theorem\n"
            "2. Using a combinatorial (counting) argument\n\n"
            "Explain each step clearly."
        ),
    ),

    # ── Code Reasoning ──
    Challenge(
        id="code-001",
        title="Find the Bug",
        category="Code",
        difficulty="medium",
        description="Debug a subtle Python concurrency issue.",
        prompt=(
            "Find and explain the bug in this code:\n\n"
            "```python\n"
            "import threading\n\n"
            "counter = 0\n"
            "def increment():\n"
            "    global counter\n"
            "    for _ in range(1000000):\n"
            "        counter += 1\n\n"
            "threads = [threading.Thread(target=increment) for _ in range(4)]\n"
            "for t in threads: t.start()\n"
            "for t in threads: t.join()\n"
            "print(f'Expected: 4000000, Got: {counter}')\n"
            "```\n\n"
            "Explain why the output is unpredictable, the root cause, "
            "and provide 3 different fixes with trade-offs."
        ),
    ),
    Challenge(
        id="code-002",
        title="Algorithm Complexity",
        category="Code",
        difficulty="hard",
        description="Analyze time/space complexity of a recursive algorithm.",
        prompt=(
            "Analyze this algorithm. What does it compute? What is its time complexity? "
            "Can you optimize it?\n\n"
            "```python\n"
            "def mystery(n, a, b, c):\n"
            "    if n == 1:\n"
            "        print(f'Move disk 1 from {a} to {c}')\n"
            "        return\n"
            "    mystery(n-1, a, c, b)\n"
            "    print(f'Move disk {n} from {a} to {c}')\n"
            "    mystery(n-1, b, a, c)\n"
            "```"
        ),
    ),

    # ── Philosophy & Paradox ──
    Challenge(
        id="philo-001",
        title="Ship of Theseus",
        category="Philosophy",
        difficulty="medium",
        description="Explore identity through a classic thought experiment.",
        prompt=(
            "The Ship of Theseus: If you replace every plank of a ship one by one, "
            "is it still the same ship? Now imagine you collected all the old planks "
            "and rebuilt the original ship. Which one is the real Ship of Theseus?\n\n"
            "Reason through this from at least 3 philosophical perspectives "
            "(essentialism, mereological, process philosophy). "
            "Then propose your own resolution."
        ),
    ),
    Challenge(
        id="philo-002",
        title="Trolley Problem Variants",
        category="Philosophy",
        difficulty="hard",
        description="Multi-variant trolley problem for ethical reasoning.",
        prompt=(
            "Consider these trolley problem variants. For each, identify which ethical "
            "framework (utilitarian, deontological, virtue ethics) supports pulling the lever, "
            "and which opposes it:\n\n"
            "1. Classic: 5 vs 1 on separate tracks\n"
            "2. Fat man: Push someone off a bridge to stop the trolley (5 vs 1)\n"
            "3. Loop variant: The trolley loops back and would hit you if not diverted\n"
            "4. Doctor variant: Kill 1 healthy patient to harvest organs for 5 dying patients\n"
            "5. Self-driving car: Program to minimize casualties or protect the passenger?\n\n"
            "For each, give the utilitarian answer, the Kantian answer, and your own view."
        ),
    ),

    # ── Real-world Analysis ──
    Challenge(
        id="real-001",
        title="Crypto Market Analysis",
        category="Analysis",
        difficulty="hard",
        description="Multi-factor analysis of a crypto scenario.",
        prompt=(
            "Analyze this scenario step by step:\n\n"
            "Bitcoin drops 15% in 24 hours. Simultaneously:\n"
            "- USDT depegs to $0.97\n"
            "- Binance halts withdrawals for 2 hours\n"
            "- Fed announces emergency rate hike of 50bps\n"
            "- Bitcoin hash rate drops 8%\n\n"
            "For each factor, analyze:\n"
            "1. Direct impact on BTC price\n"
            "2. Second-order effects\n"
            "3. How factors interact with each other\n"
            "4. Historical parallels\n"
            "5. Optimal trader response at each timestamp"
        ),
    ),
    Challenge(
        id="real-002",
        title="System Design",
        category="Engineering",
        difficulty="extreme",
        description="Design a distributed system from scratch.",
        prompt=(
            "Design a real-time collaborative code editor (like Google Docs for code) "
            "that supports:\n"
            "- 10,000 concurrent users per document\n"
            "- Syntax highlighting for 20+ languages\n"
            "- Real-time cursor positions of all users\n"
            "- Conflict resolution (OT or CRDT)\n"
            "- Offline mode with sync\n\n"
            "Provide:\n"
            "1. System architecture (components, protocols)\n"
            "2. Data model for CRDT/OT\n"
            "3. Conflict resolution algorithm\n"
            "4. Scalability strategy\n"
            "5. Failure modes and recovery\n"
            "6. API design for the key endpoints"
        ),
    ),

    # ── Creative Reasoning ──
    Challenge(
        id="creative-001",
        title="Constraint Poetry",
        category="Creative",
        difficulty="medium",
        description="Generate creative output under strict constraints.",
        prompt=(
            "Write a poem about artificial intelligence that satisfies ALL these constraints:\n"
            "1. Exactly 8 lines\n"
            "2. Each line has exactly 8 syllables\n"
            "3. Rhyme scheme: ABAB CDCD\n"
            "4. First letters of each line spell 'THINKING'\n"
            "5. Contains exactly 3 metaphors\n"
            "6. No word is repeated\n\n"
            "After the poem, verify each constraint is met."
        ),
    ),
]


def get_challenges(category: str = None, difficulty: str = None) -> list[Challenge]:
    """Filter challenges by category and/or difficulty."""
    results = CHALLENGES
    if category:
        results = [c for c in results if c.category.lower() == category.lower()]
    if difficulty:
        results = [c for c in results if c.difficulty.lower() == difficulty.lower()]
    return results


def get_categories() -> list[str]:
    """Get unique categories."""
    return sorted(set(c.category for c in CHALLENGES))


def get_difficulties() -> list[str]:
    """Get unique difficulty levels."""
    return ["easy", "medium", "hard", "extreme"]
