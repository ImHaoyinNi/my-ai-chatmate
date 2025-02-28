import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import datetime
import random


@dataclass
class InteractionData:
    """Captures data from a single interaction"""
    timestamp: datetime.datetime
    user_input: str
    ai_response: str
    user_engagement_score: float  # 0-1 scale of user engagement
    conversation_duration: float  # in seconds
    topic_entities: List[str]
    emotional_valence: float  # -1 to 1 scale
    user_feedback: Optional[float] = None  # explicit rating if provided


@dataclass
class PersonalityVector:
    """Represents the AI personality as a vector of traits"""
    # Core personality dimensions (based on psychological models)
    warmth: float  # 0-1 scale
    assertiveness: float  # 0-1 scale
    openness: float  # 0-1 scale
    conscientiousness: float  # 0-1 scale
    humor: float  # 0-1 scale
    empathy: float  # 0-1 scale

    # Communication style parameters
    verbosity: float  # 0-1 scale
    formality: float  # 0-1 scale
    complexity: float  # 0-1 scale
    emotionality: float  # 0-1 scale

    # Relationship parameters
    intimacy_comfort: float  # 0-1 scale
    disclosure_level: float  # 0-1 scale

    def to_vector(self) -> np.ndarray:
        """Convert personality to numpy vector for computation"""
        return np.array([
            self.warmth, self.assertiveness, self.openness,
            self.conscientiousness, self.humor, self.empathy,
            self.verbosity, self.formality, self.complexity,
            self.emotionality, self.intimacy_comfort, self.disclosure_level
        ])

    @classmethod
    def from_vector(cls, vector: np.ndarray) -> 'PersonalityVector':
        """Create personality from vector representation"""
        return cls(
            warmth=float(vector[0]),
            assertiveness=float(vector[1]),
            openness=float(vector[2]),
            conscientiousness=float(vector[3]),
            humor=float(vector[4]),
            empathy=float(vector[5]),
            verbosity=float(vector[6]),
            formality=float(vector[7]),
            complexity=float(vector[8]),
            emotionality=float(vector[9]),
            intimacy_comfort=float(vector[10]),
            disclosure_level=float(vector[11])
        )

    def mutate(self, mutation_rate: float = 0.05) -> 'PersonalityVector':
        """Create a slightly mutated version of this personality"""
        vector = self.to_vector()
        # Apply random mutations within bounds
        mutations = np.random.normal(0, mutation_rate, vector.shape)
        new_vector = np.clip(vector + mutations, 0.0, 1.0)
        return self.from_vector(new_vector)


class TopicModel:
    """Models topics of interest and knowledge areas"""

    def __init__(self):
        self.topics = {}  # topic_id -> interest_level (0-1)
        self.topic_connections = {}  # topic_id -> {related_topic_id -> strength}

    def update_from_interaction(self, interaction: InteractionData) -> None:
        """Update topic model based on an interaction"""
        # Extract topics from interaction
        for topic in interaction.topic_entities:
            # Update existing topics
            if topic in self.topics:
                # Increase interest level based on engagement
                current = self.topics[topic]
                self.topics[topic] = min(1.0, current + (0.1 * interaction.user_engagement_score))
            else:
                # Add new topic with initial interest level
                self.topics[topic] = 0.5

            # Update topic connections
            if topic not in self.topic_connections:
                self.topic_connections[topic] = {}

            # Connect this topic with other topics in this interaction
            for other_topic in interaction.topic_entities:
                if topic != other_topic:
                    if other_topic not in self.topic_connections[topic]:
                        self.topic_connections[topic][other_topic] = 0.1
                    else:
                        # Strengthen connection
                        current = self.topic_connections[topic][other_topic]
                        self.topic_connections[topic][other_topic] = min(1.0, current + 0.05)

    def get_recommended_topics(self, n: int = 3) -> List[str]:
        """Get highest interest topics for conversation initiation"""
        sorted_topics = sorted(self.topics.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_topics[:n]]

    def expand_knowledge(self) -> List[str]:
        """Identify topics to autonomously learn more about"""
        # Find topics with high interest but few connections
        candidates = []
        for topic, interest in self.topics.items():
            if interest > 0.7:
                connection_count = len(self.topic_connections.get(topic, {}))
                if connection_count < 3:
                    candidates.append((topic, interest))

        return [c[0] for c in sorted(candidates, key=lambda x: x[1], reverse=True)]


class MemorySystem:
    """Long-term memory system for the symbiotic AI"""

    def __init__(self, max_episodic_memories: int = 500):
        self.episodic_memories = []  # List of specific interactions to remember
        self.max_episodic_memories = max_episodic_memories
        self.user_facts = {}  # Extracted facts about the user
        self.shared_experiences = []  # Special moments between AI and user

    def process_interaction(self, interaction: InteractionData) -> None:
        """Process an interaction for memory storage"""
        # Decide if this interaction should be stored as an episodic memory
        importance = self._calculate_importance(interaction)

        if importance > 0.7 or len(self.episodic_memories) < 50:
            self.episodic_memories.append({
                "interaction": interaction,
                "importance": importance,
                "last_recalled": None,
                "recall_count": 0
            })

            # Keep memory size under control
            if len(self.episodic_memories) > self.max_episodic_memories:
                # Remove least important memories
                self.episodic_memories.sort(key=lambda x: x["importance"])
                self.episodic_memories = self.episodic_memories[-self.max_episodic_memories:]

        # Extract potential user facts (in a real system, this would use NLP)
        # This is a simplified placeholder implementation
        pass

    def _calculate_importance(self, interaction: InteractionData) -> float:
        """Calculate the importance of an interaction for memory"""
        importance = 0.0

        # Emotional interactions are more important
        importance += abs(interaction.emotional_valence) * 0.3

        # User engagement increases importance
        importance += interaction.user_engagement_score * 0.3

        # Explicit feedback makes it more important
        if interaction.user_feedback is not None:
            importance += 0.3

        # Longer interactions might be more important
        if interaction.conversation_duration > 120:  # 2+ minutes
            importance += 0.1

        return min(importance, 1.0)

    def get_relevant_memories(self, current_topics: List[str], n: int = 3) -> List[Dict]:
        """Retrieve memories relevant to current conversation topics"""
        scored_memories = []

        for memory in self.episodic_memories:
            interaction = memory["interaction"]

            # Calculate relevance score based on topic overlap
            topic_overlap = len(set(interaction.topic_entities) & set(current_topics))
            relevance = topic_overlap * 0.2 + memory["importance"] * 0.8

            # Reduce score for frequently recalled memories
            recall_penalty = min(memory["recall_count"] * 0.1, 0.5) if memory["recall_count"] else 0

            # Recency bonus for recent memories
            days_ago = (datetime.datetime.now() - interaction.timestamp).days
            recency_bonus = max(0, 0.3 - (days_ago * 0.01))

            final_score = relevance - recall_penalty + recency_bonus
            scored_memories.append((memory, final_score))

        # Get top memories by score
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        top_memories = [m[0] for m in scored_memories[:n]]

        # Update recall statistics
        for memory in top_memories:
            memory["last_recalled"] = datetime.datetime.now()
            memory["recall_count"] = memory.get("recall_count", 0) + 1

        return top_memories


class SymbioticEvolutionSystem:
    """Core system for evolving an AI in symbiosis with the user"""

    def __init__(self, initial_personality: PersonalityVector):
        self.current_personality = initial_personality
        self.personality_history = [(datetime.datetime.now(), initial_personality)]
        self.topic_model = TopicModel()
        self.memory_system = MemorySystem()
        self.recent_interactions = []
        self.evolution_rate = 0.05  # Base evolution rate
        self.adaptation_vectors = {}  # Stored adaptation vectors for personality traits

    def record_interaction(self, interaction: InteractionData) -> None:
        """Record a new interaction with the user"""
        self.recent_interactions.append(interaction)
        # Keep limited history of recent interactions
        if len(self.recent_interactions) > 100:
            self.recent_interactions = self.recent_interactions[-100:]

        # Update topic model
        self.topic_model.update_from_interaction(interaction)

        # Process for memory
        self.memory_system.process_interaction(interaction)

        # Potentially evolve personality based on this interaction
        self._consider_evolution()

    def _consider_evolution(self) -> None:
        """Consider evolving the personality based on recent interactions"""
        # Only evolve after sufficient interactions
        if len(self.recent_interactions) < 5:
            return

        # Calculate time since last evolution
        last_evolution_time = self.personality_history[-1][0]
        time_since_evolution = (datetime.datetime.now() - last_evolution_time).total_seconds()

        # Don't evolve too frequently (minimum 24 hours between evolutions)
        if time_since_evolution < 86400:
            return

        # Random chance of evolution (50% if conditions are met)
        if random.random() < 0.5:
            self._evolve_personality()

    def _evolve_personality(self) -> None:
        """Evolve the AI personality based on interaction patterns"""
        # Get recent interactions for analysis
        recent = self.recent_interactions[-20:]  # Last 20 interactions

        # Calculate adaptation vector based on user engagement
        adaptation_vector = np.zeros(12)  # Same length as personality vector

        # 1. Analyze engagement patterns
        engagement_scores = [i.user_engagement_score for i in recent]
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0

        # 2. If engagement is low, make larger adaptations
        adaptation_magnitude = 0.1 if avg_engagement < 0.5 else 0.05

        # 3. Analyze which personality aspects to adapt
        # This would use more sophisticated analysis in a real system
        # Here we use a simplified approach:

        # Example: If emotional responses get better engagement, increase emotionality
        emotional_interactions = [(i.user_engagement_score, i.emotional_valence) for i in recent]
        if emotional_interactions:
            emotional_correlation = np.corrcoef(
                [e[0] for e in emotional_interactions],
                [abs(e[1]) for e in emotional_interactions]
            )[0, 1] if len(emotional_interactions) > 1 else 0

            if not np.isnan(emotional_correlation) and emotional_correlation > 0.2:
                # Positive correlation - more emotional responses get better engagement
                adaptation_vector[9] = adaptation_magnitude  # Increase emotionality

        # Example: Adapt verbosity based on conversation duration
        durations = [i.conversation_duration for i in recent]
        avg_duration = sum(durations) / len(durations) if durations else 0
        if avg_duration < 60:  # Short conversations
            # Try increasing verbosity to extend conversations
            adaptation_vector[6] = adaptation_magnitude
        elif avg_duration > 300:  # Very long conversations
            # Maybe try being more concise
            adaptation_vector[6] = -adaptation_magnitude

        # 4. Incorporate random exploration to find better adaptations
        random_exploration = np.random.normal(0, 0.02, 12)  # Small random changes
        adaptation_vector += random_exploration

        # 5. Apply the adaptation to the personality
        personality_vector = self.current_personality.to_vector()
        new_vector = np.clip(personality_vector + adaptation_vector, 0.0, 1.0)
        new_personality = PersonalityVector.from_vector(new_vector)

        # 6. Store the new personality
        self.current_personality = new_personality
        self.personality_history.append((datetime.datetime.now(), new_personality))

        # 7. Store this adaptation vector for learning
        self.adaptation_vectors[datetime.datetime.now()] = {
            "vector": adaptation_vector,
            "prior_engagement": avg_engagement
        }

    def generate_conversation_starter(self) -> Tuple[str, Dict]:
        """Generate a conversation starter based on current knowledge"""
        # Get recommended topics
        topics = self.topic_model.get_recommended_topics(5)

        # Select topic with some randomness
        if random.random() < 0.8 and topics:  # 80% use recommended topics
            weights = [0.5, 0.25, 0.15, 0.07, 0.03][:len(topics)]  # Favor higher interest
            selected_topic = random.choices(topics, weights=weights[:len(topics)])[0]
        else:
            # 20% chance to explore a new topic or fallback if no topics
            general_topics = ["current events", "personal interests", "recent activities",
                              "future plans", "entertainment", "philosophical questions"]
            selected_topic = random.choice(general_topics)

        # Get relevant memories for context
        memories = self.memory_system.get_relevant_memories([selected_topic], 2)
        memory_context = [m["interaction"].ai_response for m in memories]

        # Generate starter based on topic and personality
        # This is where you'd use an LLM with appropriate prompt engineering
        # For this example, we'll just return the topic and context
        return selected_topic, {
            "personality": self.current_personality,
            "memory_context": memory_context
        }

    def get_evolution_summary(self) -> Dict:
        """Get a summary of how the AI has evolved"""
        if len(self.personality_history) < 2:
            return {"evolution": "Insufficient data for evolution summary"}

        initial = self.personality_history[0][1]
        current = self.personality_history[-1][1]

        # Calculate changes in each dimension
        initial_vec = initial.to_vector()
        current_vec = current.to_vector()
        changes = current_vec - initial_vec

        # Get dimensions with largest changes
        trait_names = [
            "warmth", "assertiveness", "openness", "conscientiousness",
            "humor", "empathy", "verbosity", "formality",
            "complexity", "emotionality", "intimacy_comfort", "disclosure_level"
        ]

        changes_dict = {trait_names[i]: float(changes[i]) for i in range(len(trait_names))}
        sorted_changes = sorted(changes_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        # Get evolution timeline
        timeline = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "personality": {
                    trait_names[i]: float(personality.to_vector()[i])
                    for i in range(len(trait_names))
                }
            }
            for date, personality in self.personality_history
        ]

        return {
            "top_changes": sorted_changes[:3],
            "evolution_count": len(self.personality_history) - 1,
            "first_evolution": self.personality_history[1][0] if len(self.personality_history) > 1 else None,
            "latest_evolution": self.personality_history[-1][0],
            "timeline": timeline
        }


# Example Usage

# Initialize with default personality
initial_personality = PersonalityVector(
    warmth=0.7,
    assertiveness=0.4,
    openness=0.8,
    conscientiousness=0.6,
    humor=0.5,
    empathy=0.8,
    verbosity=0.6,
    formality=0.3,
    complexity=0.5,
    emotionality=0.6,
    intimacy_comfort=0.4,
    disclosure_level=0.5
)

evolution_system = SymbioticEvolutionSystem(initial_personality)


if __name__ == "__main__":
    # Simulate some interactions
    for i in range(10):
        # Create simulated interaction data
        interaction = InteractionData(
            timestamp=datetime.datetime.now() - datetime.timedelta(days=10 - i),
            user_input=f"Simulated user input {i}",
            ai_response=f"Simulated AI response {i}",
            user_engagement_score=random.random(),  # Random engagement 0-1
            conversation_duration=random.randint(30, 300),  # 30s to 5min
            topic_entities=random.sample(["music", "art", "technology", "science", "philosophy", "food"], 2),
            emotional_valence=random.uniform(-0.5, 0.8),  # Emotional content
            user_feedback=random.random() if random.random() > 0.7 else None  # Occasional feedback
        )

        # Record the interaction
        evolution_system.record_interaction(interaction)

    # Force evolution for demonstration
    evolution_system._evolve_personality()

    # Get a conversation starter
    topic, context = evolution_system.generate_conversation_starter()
    print(f"Conversation starter topic: {topic}")
    print(f"With context: {context}")

    # Get evolution summary
    summary = evolution_system.get_evolution_summary()
    print(f"Evolution summary: {summary}")