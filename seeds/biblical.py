"""Biblical Forks: Judeo-Christian ideological divergences.

These tensions have shaped Western civilization for millennia.
Many contemporary political divides trace back to these ancient forks.

"There is nothing new under the sun." - Ecclesiastes 1:9
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.forks import Fork, ForkLevel
from models.position import Domain


BIBLICAL_FORKS = [
    # ═══ CREATION & NATURE ═══
    Fork(
        id="imago_dei",
        question="What is humanity's relationship to creation?",
        option_a="Stewards—caretakers of God's creation, responsible for it",
        option_b="Dominion—rulers over creation, given to us for use",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["franciscan", "ecological", "stewardship"],
        traditions_b=["dominionist", "prosperity", "anthropocentric"],
        polarization=0.7,
        importance=0.85
    ),
    Fork(
        id="original_sin",
        question="What is the nature of human sinfulness?",
        option_a="Total depravity—humans cannot choose good without grace",
        option_b="Wounded nature—humans retain capacity for good, need help",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["calvinist", "augustinian", "reformed"],
        traditions_b=["catholic", "orthodox", "arminian"],
        polarization=0.85,
        importance=0.95
    ),
    Fork(
        id="free_will",
        question="Do humans have free will?",
        option_a="Predestination—God ordains all, human choice is illusion",
        option_b="Libertarian free will—humans genuinely choose their fate",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.METAPHYSICS,
        parent_fork_id="original_sin",
        traditions_a=["calvinist", "fatalist", "determinist"],
        traditions_b=["catholic", "arminian", "open_theist"],
        polarization=0.9,
        importance=0.9
    ),

    # ═══ LAW & GRACE ═══
    Fork(
        id="law_gospel",
        question="What is the relationship between Law and Gospel?",
        option_a="Continuity—Law still binding, fulfilled not abolished",
        option_b="Discontinuity—Grace supersedes Law, new covenant",
        level=ForkLevel.AXIOM,
        domain=Domain.GOVERNANCE,
        traditions_a=["torah_observant", "theonomy", "judaizing"],
        traditions_b=["pauline", "antinomian", "dispensationalist"],
        polarization=0.8,
        importance=0.85
    ),
    Fork(
        id="works_faith",
        question="How is salvation achieved?",
        option_a="Faith alone—sola fide, works are fruit not cause",
        option_b="Faith and works—both required, cooperate with grace",
        level=ForkLevel.AXIOM,
        domain=Domain.METAPHYSICS,
        parent_fork_id="law_gospel",
        traditions_a=["protestant", "lutheran", "reformed"],
        traditions_b=["catholic", "orthodox", "james_emphasis"],
        polarization=0.85,
        importance=0.9
    ),

    # ═══ AUTHORITY & TRADITION ═══
    Fork(
        id="sola_scriptura",
        question="What is the source of religious authority?",
        option_a="Scripture alone—Bible is sole infallible authority",
        option_b="Scripture and Tradition—Church interprets, Magisterium guides",
        level=ForkLevel.AXIOM,
        domain=Domain.EPISTEMOLOGY,
        traditions_a=["protestant", "evangelical", "fundamentalist"],
        traditions_b=["catholic", "orthodox", "high_church"],
        polarization=0.9,
        importance=0.9
    ),
    Fork(
        id="church_authority",
        question="Where does church authority reside?",
        option_a="Hierarchy—bishops, Pope, apostolic succession",
        option_b="Congregation—priesthood of all believers, local autonomy",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.GOVERNANCE,
        parent_fork_id="sola_scriptura",
        traditions_a=["catholic", "orthodox", "episcopal"],
        traditions_b=["baptist", "congregationalist", "anabaptist"],
        polarization=0.85,
        importance=0.8
    ),

    # ═══ KINGDOM & WORLD ═══
    Fork(
        id="two_kingdoms",
        question="What is the relationship between Church and State?",
        option_a="Separation—two kingdoms, spiritual and temporal distinct",
        option_b="Integration—Christendom, throne and altar united",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.GOVERNANCE,
        traditions_a=["lutheran", "baptist", "anabaptist"],
        traditions_b=["catholic_integralist", "theocratic", "constantinian"],
        polarization=0.8,
        importance=0.85
    ),
    Fork(
        id="eschatology",
        question="What is the trajectory of history?",
        option_a="Premillennial—world worsens, Christ returns to fix it",
        option_b="Postmillennial—world improves, we build the Kingdom",
        level=ForkLevel.AXIOM,
        domain=Domain.METAPHYSICS,
        traditions_a=["dispensationalist", "pessimist", "rapture"],
        traditions_b=["reconstructionist", "optimist", "dominionist"],
        polarization=0.75,
        importance=0.8
    ),
    Fork(
        id="worldly_engagement",
        question="How should believers engage with worldly power?",
        option_a="Withdrawal—be in world not of it, separate community",
        option_b="Transformation—redeem culture, engage institutions",
        level=ForkLevel.DOMAIN,
        domain=Domain.GOVERNANCE,
        parent_fork_id="two_kingdoms",
        traditions_a=["anabaptist", "amish", "monastic"],
        traditions_b=["kuyperian", "cultural_mandate", "moral_majority"],
        polarization=0.7,
        importance=0.75
    ),

    # ═══ WEALTH & POVERTY ═══
    Fork(
        id="wealth",
        question="What is the moral status of wealth?",
        option_a="Suspicion—easier for camel through needle, blessed are poor",
        option_b="Blessing—prosperity as sign of God's favor, stewardship",
        level=ForkLevel.DOMAIN,
        domain=Domain.ECONOMICS,
        traditions_a=["franciscan", "liberation", "monastic"],
        traditions_b=["prosperity_gospel", "calvinist_work_ethic", "puritan"],
        polarization=0.8,
        importance=0.75
    ),
    Fork(
        id="jubilee",
        question="Should debts be forgiven and wealth redistributed?",
        option_a="Yes—Jubilee, sabbatical economics, structural reset",
        option_b="No—contracts sacred, charity voluntary not mandated",
        level=ForkLevel.POLICY,
        domain=Domain.ECONOMICS,
        parent_fork_id="wealth",
        traditions_a=["liberation", "catholic_social", "anabaptist"],
        traditions_b=["libertarian_christian", "prosperity", "conservative"],
        polarization=0.75,
        importance=0.7
    ),

    # ═══ JUSTICE & MERCY ═══
    Fork(
        id="justice_mercy",
        question="When justice and mercy conflict, which prevails?",
        option_a="Justice—sin must be punished, atonement required",
        option_b="Mercy—forgiveness freely given, restorative not retributive",
        level=ForkLevel.AXIOM,
        domain=Domain.GOVERNANCE,
        traditions_a=["penal_substitution", "calvinist", "conservative"],
        traditions_b=["christus_victor", "universalist", "progressive"],
        polarization=0.85,
        importance=0.85
    ),
    Fork(
        id="punishment",
        question="What is the purpose of punishment?",
        option_a="Retribution—just deserts, eye for eye, wages of sin",
        option_b="Restoration—reconciliation, healing, redemption",
        level=ForkLevel.POLICY,
        domain=Domain.GOVERNANCE,
        parent_fork_id="justice_mercy",
        traditions_a=["conservative", "law_and_order", "traditional"],
        traditions_b=["restorative_justice", "mennonite", "progressive"],
        polarization=0.8,
        importance=0.7
    ),

    # ═══ GENDER & FAMILY ═══
    Fork(
        id="gender_roles",
        question="What are proper gender roles?",
        option_a="Complementarian—distinct roles, male headship, female submission",
        option_b="Egalitarian—equal roles, mutual submission, no hierarchy",
        level=ForkLevel.DOMAIN,
        domain=Domain.SOCIAL,
        traditions_a=["complementarian", "traditional", "conservative"],
        traditions_b=["egalitarian", "progressive", "feminist_christian"],
        polarization=0.9,
        importance=0.75
    ),

    # ═══ CHOSEN PEOPLE & UNIVERSALISM ═══
    Fork(
        id="election",
        question="Who are God's people?",
        option_a="Particular—elect chosen, Israel special, remnant saved",
        option_b="Universal—all called, grafted in, God desires all saved",
        level=ForkLevel.AXIOM,
        domain=Domain.METAPHYSICS,
        traditions_a=["calvinist", "zionist_christian", "particularist"],
        traditions_b=["universalist", "inclusivist", "arminian"],
        polarization=0.85,
        importance=0.85
    ),
    Fork(
        id="israel_church",
        question="What is the relationship between Israel and the Church?",
        option_a="Replacement—Church is new Israel, promises transferred",
        option_b="Distinction—Israel still chosen, separate prophetic destiny",
        level=ForkLevel.DOMAIN,
        domain=Domain.FOREIGN_POLICY,
        parent_fork_id="election",
        traditions_a=["supersessionist", "covenant", "amillennial"],
        traditions_b=["dispensationalist", "zionist_christian", "premillennial"],
        polarization=0.8,
        importance=0.7
    ),

    # ═══ VIOLENCE & PEACE ═══
    Fork(
        id="violence",
        question="Is violence ever justified for Christians?",
        option_a="Pacifism—turn other cheek, enemy love absolute, never kill",
        option_b="Just War—defense of innocent, proper authority, last resort",
        level=ForkLevel.DOMAIN,
        domain=Domain.FOREIGN_POLICY,
        traditions_a=["anabaptist", "quaker", "mennonite"],
        traditions_b=["augustinian", "aquinas", "just_war"],
        polarization=0.85,
        importance=0.8
    ),
]
