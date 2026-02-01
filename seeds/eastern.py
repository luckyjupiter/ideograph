"""Eastern Forks: Buddhist, Confucian, Hindu, and Daoist divergences.

These traditions offer alternative axes of ideological variation
that Western-centric models miss entirely.

"The Tao that can be told is not the eternal Tao." - Laozi
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.forks import Fork, ForkLevel
from models.position import Domain


EASTERN_FORKS = [
    # ═══════════════════════════════════════════════════════════════
    # BUDDHIST FORKS
    # ═══════════════════════════════════════════════════════════════

    Fork(
        id="self_existence",
        question="Does the self exist?",
        option_a="Anatman—no self, bundle of aggregates, illusion of continuity",
        option_b="Atman—eternal self exists, witness consciousness, soul",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["buddhist", "madhyamaka", "yogacara"],
        traditions_b=["hindu", "vedanta", "jain"],
        polarization=0.95,
        importance=1.0
    ),
    Fork(
        id="nirvana_samsara",
        question="What is the relationship between nirvana and samsara?",
        option_a="Identical—nirvana is samsara seen correctly, nothing to escape",
        option_b="Distinct—nirvana is escape from samsara, transcendence required",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.METAPHYSICS,
        parent_fork_id="self_existence",
        traditions_a=["mahayana", "zen", "madhyamaka"],
        traditions_b=["theravada", "early_buddhism", "renunciant"],
        polarization=0.8,
        importance=0.85
    ),
    Fork(
        id="buddha_nature",
        question="Do all beings have Buddha-nature?",
        option_a="Yes—tathagatagarbha, enlightenment inherent, just uncover",
        option_b="No—must be cultivated, gradual path, not pre-existing",
        level=ForkLevel.AXIOM,
        domain=Domain.METAPHYSICS,
        traditions_a=["zen", "vajrayana", "huayan"],
        traditions_b=["theravada", "madhyamaka_strict", "gradualist"],
        polarization=0.75,
        importance=0.8
    ),
    Fork(
        id="sudden_gradual",
        question="Is enlightenment sudden or gradual?",
        option_a="Sudden—instant awakening, no stages, already enlightened",
        option_b="Gradual—step by step, stages of the path, cultivation",
        level=ForkLevel.DOMAIN,
        domain=Domain.METAPHYSICS,
        parent_fork_id="buddha_nature",
        traditions_a=["zen", "dzogchen", "southern_chan"],
        traditions_b=["theravada", "tibetan_lam_rim", "northern_chan"],
        polarization=0.8,
        importance=0.75
    ),
    Fork(
        id="arhat_bodhisattva",
        question="What is the ideal spiritual goal?",
        option_a="Bodhisattva—postpone nirvana to save all beings, compassion first",
        option_b="Arhat—personal liberation, escape samsara, wisdom first",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        traditions_a=["mahayana", "vajrayana", "engaged_buddhism"],
        traditions_b=["theravada", "early_buddhism", "forest_tradition"],
        polarization=0.85,
        importance=0.85
    ),
    Fork(
        id="engaged_buddhism",
        question="Should Buddhism engage with politics/society?",
        option_a="Yes—transform society, Buddhist economics, social justice",
        option_b="No—focus on individual liberation, politics is samsara",
        level=ForkLevel.DOMAIN,
        domain=Domain.GOVERNANCE,
        parent_fork_id="arhat_bodhisattva",
        traditions_a=["engaged_buddhism", "thich_nhat_hanh", "ambedkar"],
        traditions_b=["forest_tradition", "monastic", "contemplative"],
        polarization=0.7,
        importance=0.7
    ),

    # ═══════════════════════════════════════════════════════════════
    # CONFUCIAN/CHINESE FORKS
    # ═══════════════════════════════════════════════════════════════

    Fork(
        id="human_nature_chinese",
        question="What is human nature?",
        option_a="Good—Mencius, innate moral sprouts, just need nurturing",
        option_b="Evil—Xunzi, selfish by nature, need ritual/law to civilize",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["mencian", "neo_confucian", "idealist"],
        traditions_b=["xunzi", "legalist", "realist"],
        polarization=0.9,
        importance=0.95
    ),
    Fork(
        id="li_fa",
        question="What should govern society?",
        option_a="Li (ritual/custom)—internalized virtue, moral example",
        option_b="Fa (law)—external rules, rewards and punishments",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.GOVERNANCE,
        parent_fork_id="human_nature_chinese",
        traditions_a=["confucian", "ru", "virtue_ethics"],
        traditions_b=["legalist", "fajia", "authoritarian"],
        polarization=0.85,
        importance=0.9
    ),
    Fork(
        id="junzi_cultivation",
        question="How does one become a junzi (exemplary person)?",
        option_a="Study—learning classics, scholarship, examination",
        option_b="Practice—moral action, filial piety, daily cultivation",
        level=ForkLevel.DOMAIN,
        domain=Domain.SOCIAL,
        parent_fork_id="li_fa",
        traditions_a=["scholarly", "imperial_examination", "literary"],
        traditions_b=["practical", "neo_confucian", "wang_yangming"],
        polarization=0.6,
        importance=0.7
    ),
    Fork(
        id="confucian_daoist",
        question="Should we follow social conventions or nature?",
        option_a="Conventions—ren (benevolence), li (ritual), social harmony",
        option_b="Nature—wu wei, follow the Dao, reject artificial distinctions",
        level=ForkLevel.AXIOM,
        domain=Domain.GOVERNANCE,
        traditions_a=["confucian", "ru", "social"],
        traditions_b=["daoist", "laozi", "zhuangzi"],
        polarization=0.85,
        importance=0.9
    ),
    Fork(
        id="action_inaction",
        question="What is the proper mode of action?",
        option_a="Wu wei—non-action, effortless action, flow with nature",
        option_b="You wei—purposive action, striving, making effort",
        level=ForkLevel.AXIOM,
        domain=Domain.GOVERNANCE,
        parent_fork_id="confucian_daoist",
        traditions_a=["daoist", "zhuangzi", "quietist"],
        traditions_b=["confucian", "mohist", "legalist"],
        polarization=0.8,
        importance=0.85
    ),
    Fork(
        id="universalism_particularism",
        question="Should we love all equally or prioritize family?",
        option_a="Jian ai (universal love)—equal concern for all, impartial",
        option_b="Graded love—family first, then community, then strangers",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        traditions_a=["mohist", "utilitarian", "impartialist"],
        traditions_b=["confucian", "family_values", "communitarian"],
        polarization=0.8,
        importance=0.8
    ),

    # ═══════════════════════════════════════════════════════════════
    # HINDU FORKS
    # ═══════════════════════════════════════════════════════════════

    Fork(
        id="brahman_atman",
        question="What is the relationship between Brahman and Atman?",
        option_a="Advaita—non-dual, Atman IS Brahman, difference is illusion",
        option_b="Dvaita—dual, Atman distinct from Brahman, relationship real",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["advaita_vedanta", "shankara", "non_dual"],
        traditions_b=["dvaita_vedanta", "madhva", "vaishnava"],
        polarization=0.9,
        importance=1.0
    ),
    Fork(
        id="maya",
        question="What is the status of the world?",
        option_a="Maya/illusion—world is appearance, only Brahman real",
        option_b="Real—world is Brahman's lila (play), genuinely exists",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.METAPHYSICS,
        parent_fork_id="brahman_atman",
        traditions_a=["advaita", "shankara", "illusionist"],
        traditions_b=["vishishtadvaita", "ramanuja", "realist"],
        polarization=0.85,
        importance=0.85
    ),
    Fork(
        id="moksha_path",
        question="What is the path to liberation?",
        option_a="Jnana—knowledge, discrimination, inquiry into self",
        option_b="Bhakti—devotion, surrender, love of God",
        level=ForkLevel.AXIOM,
        domain=Domain.METAPHYSICS,
        traditions_a=["jnana_yoga", "advaita", "philosophical"],
        traditions_b=["bhakti", "vaishnava", "devotional"],
        polarization=0.75,
        importance=0.85
    ),
    Fork(
        id="karma_path",
        question="Can action lead to liberation?",
        option_a="Yes—karma yoga, act without attachment, duty without desire",
        option_b="No—renounce action, sannyasa, withdraw from world",
        level=ForkLevel.DOMAIN,
        domain=Domain.SOCIAL,
        parent_fork_id="moksha_path",
        traditions_a=["gita", "karma_yoga", "engaged"],
        traditions_b=["sannyasa", "monastic", "renunciant"],
        polarization=0.7,
        importance=0.75
    ),
    Fork(
        id="varnashrama",
        question="Is the caste system spiritually valid?",
        option_a="Yes—dharma varies by varna, cosmic order, svadharma",
        option_b="No—spiritual equality, caste is social not metaphysical",
        level=ForkLevel.DOMAIN,
        domain=Domain.SOCIAL,
        traditions_a=["traditional", "brahmanical", "conservative"],
        traditions_b=["reformist", "bhakti_egalitarian", "ambedkarite"],
        polarization=0.9,
        importance=0.8
    ),
    Fork(
        id="avatar",
        question="Does God incarnate in the world?",
        option_a="Yes—avatara, God descends to restore dharma, Krishna/Rama",
        option_b="No—Brahman is formless, personal God is lower truth",
        level=ForkLevel.DOMAIN,
        domain=Domain.METAPHYSICS,
        parent_fork_id="brahman_atman",
        traditions_a=["vaishnava", "puranic", "devotional"],
        traditions_b=["advaita", "philosophical", "nirguna_brahman"],
        polarization=0.75,
        importance=0.7
    ),

    # ═══════════════════════════════════════════════════════════════
    # CROSS-TRADITION FORKS
    # ═══════════════════════════════════════════════════════════════

    Fork(
        id="emptiness_fullness",
        question="Is ultimate reality empty or full?",
        option_a="Empty—sunyata, no inherent existence, beyond concepts",
        option_b="Full—plenum, infinite being, consciousness, bliss",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["madhyamaka", "zen", "apophatic"],
        traditions_b=["vedanta", "tantric", "cataphatic"],
        polarization=0.85,
        importance=0.9
    ),
    Fork(
        id="individual_liberation",
        question="Is liberation individual or collective?",
        option_a="Individual—each attains alone, personal journey",
        option_b="Collective—all beings together, interbeing, collective karma",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        traditions_a=["theravada", "jain", "individualist"],
        traditions_b=["mahayana", "engaged", "communal"],
        polarization=0.75,
        importance=0.8
    ),
    Fork(
        id="world_affirmation",
        question="Should we affirm or negate the world?",
        option_a="Affirm—tantra, embrace experience, transform not escape",
        option_b="Negate—renounce, transcend, world is suffering/illusion",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        traditions_a=["tantric", "daoist", "confucian"],
        traditions_b=["renunciant", "monastic", "gnostic"],
        polarization=0.8,
        importance=0.85
    ),
    Fork(
        id="teacher_authority",
        question="How important is the guru/teacher?",
        option_a="Essential—transmission, lineage, surrender to master",
        option_b="Optional—self-inquiry, texts sufficient, be your own lamp",
        level=ForkLevel.DOMAIN,
        domain=Domain.EPISTEMOLOGY,
        traditions_a=["vajrayana", "vedanta", "sufi"],
        traditions_b=["zen_iconoclast", "theravada", "jnana"],
        polarization=0.7,
        importance=0.7
    ),
    Fork(
        id="meditation_ritual",
        question="What is the primary practice?",
        option_a="Meditation—inner cultivation, direct experience, jhana/samadhi",
        option_b="Ritual—puja, offerings, mantra, external devotion",
        level=ForkLevel.DOMAIN,
        domain=Domain.SOCIAL,
        traditions_a=["zen", "theravada", "vipassana"],
        traditions_b=["tantric", "bhakti", "ritual"],
        polarization=0.7,
        importance=0.7
    ),
]
