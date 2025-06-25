################################################################################
# MindScript Language library
# (c) 2024 DAIOS Technologies Ltd.
################################################################################


# Named entity reconignition.
#############################

let nerExamples = [
    [
        "Apple Inc. announced a new iPhone model at their headquarters in Cupertino on September 14, 2021.",
        [
            {text: "Apple Inc.", entity: "Organization"},
            {text: "iPhone", entity: "Product"},
            {text: "Cupertino", entity: "Location"},
            {text: "September 14, 2021", entity: "Date"}
        ]
    ],
    [
        "The research conducted by Dr. Jane Smith at Stanford University focuses on the impact of climate change on marine biodiversity.",
        [
            {text: "Dr. Jane Smith", entity: "Person"},
            {text: "Stanford University", entity: "Organization"},
            {text: "climate change", entity: "Concept"},
            {text: "marine biodiversity", entity: "Concept"}
        ]
    ],
    [
        "Had an amazing time visiting the Eiffel Tower in Paris last summer!",
        [
            {text: "Eiffel Tower", entity: "Location"},
            {text: "Paris", entity: "Location"},
            {text: "last summer", entity: "Date"}
        ]
    ],
    [
        "In Q1 2022, Google reported a 25% increase in revenue, largely driven by growth in their cloud computing division.",
        [
            {text: "Q1 2022", entity: "Date"},
            {text: "Google", entity: "Organization"},
            {text: "25%", entity: "Percentage"},
            {text: "cloud computing division", entity: "Service"}
        ]
    ],
    [
        "The Treaty of Versailles was signed on June 28, 1919, marking the end of World War I.",
        [
            {text: "Treaty of Versailles", entity: "Event"},
            {text: "June 28, 1919", entity: "Date"},
            {text: "World War I",  entity: "Event"}

        ]
    ]
]

# For almost each word in the text, identify and classify it into entities such as 
# persons, organizations, locations, dates, products, and concepts.
let ner = oracle(text: Str) -> [{text: Str, entity: Str}] from nerExamples


# PoS - Part of Speech Tagging.
###############################

let posExamples = [
    [
        "The quick brown fox jumps over the lazy dog.",
        [
            {position: 0, word: "The", tag: "Determiner"},
            {position: 1, word: "quick", tag: "Adjective"},
            {position: 2, word: "brown", tag: "Adjective"},
            {position: 3, word: "fox", tag: "Noun"},
            {position: 4, word: "jumps", tag: "Verb"},
            {position: 5, word: "over", tag: "Preposition"},
            {position: 6, word: "the", tag: "Determiner"},
            {position: 7, word: "lazy", tag: "Adjective"},
            {position: 8, word: "dog", tag: "Noun"}
        ]
    ],
    [
        "She sells seashells by the seashore.",
        [
            {position: 0, word: "She", tag: "Pronoun"},
            {position: 1, word: "sells", tag: "Verb"},
            {position: 2, word: "seashells", tag: "Noun"},
            {position: 3, word: "by", tag: "Preposition"},
            {position: 4, word: "the", tag: "Determiner"},
            {position: 5, word: "seashore", tag: "Noun"}
        ]
    ],
    [
        "He quickly ran to the store.",
        [
            {position: 0, word: "He", tag: "Pronoun"},
            {position: 1, word: "quickly", tag: "Adverb"},
            {position: 2, word: "ran", tag: "Verb"},
            {position: 3, word: "to", tag: "Preposition"},
            {position: 4, word: "the", tag: "Determiner"},
            {position: 5, word: "store", tag: "Noun"}
        ]
    ],
    [
        "They are planning a big surprise party.",
        [
            {position: 0, word: "They", tag: "Pronoun"},
            {position: 1, word: "are", tag: "Verb"},
            {position: 2, word: "planning", tag: "Verb"},
            {position: 3, word: "a", tag: "Determiner"},
            {position: 4, word: "big", tag: "Adjective"},
            {position: 5, word: "surprise", tag: "Adjective"},
            {position: 6, word: "party", tag: "Noun"}
        ]
    ],
    [
        "Reading books can expand your knowledge.",
        [
            {position: 0, word: "Reading", tag: "Verb"},
            {position: 1, word: "books", tag: "Noun"},
            {position: 2, word: "can", tag: "Modal"},
            {position: 3, word: "expand", tag: "Verb"},
            {position: 4, word: "your", tag: "Pronoun"},
            {position: 5, word: "knowledge", tag: "Noun"}
        ]
    ]
]

# For each word in a sentence, assign a part-of-speech tag, where each label
# indicates the grammatical category of each word, such as noun, verb, etc.
let pos = oracle(text: Str) -> [{position: Int, word: Str, tag: Str}] from posExamples


# Sentiment analysis.
#####################

let Sentiment = type {sentiment: Enum(Str, ["negative", "neutral", "positive"])} 

# Determine the sentiment of given text.
let sentiment = oracle(text: Str) -> Sentiment


# Language detection and translation.
#####################################

# Typical languages.
let languages = ["English", "Mandarin", "Spanish", "Hindi", "German", "Arabic", "French", "Italian"]

# Returns a language detector for the given languages.
let makeLanguageDetector = fun(langs: [Str]?) -> Str -> Str do
    if langs == null then
        langs = languages
    end
    # Detect the language the text is written in.
    oracle(text: Str) -> Enum(Str, langs)
end

# Translate the text into the target language.
let translate = oracle(text: Str, targetLang: Str) -> Str


# Text classification.
######################

# Returns a text classifier for the given categories.
let makeClassifier = fun(categories: [Str]) do
    let Categories = type Enum(Str, categories)

    # Classify the text into one of the categories.
    let classifier = oracle(text: Str) -> Categories
end

# Text summarization.

# Summarize the text.
let summarize = oracle(text: Str) -> Str


# Topic modelling.
##################

let topicExamples = [
    [
        "The economy is improving. Unemployment rates are falling and the stock market is rising.",
        ["economy", "unemployment", "stock market"]
    ],
    [
        "Climate change impacts include rising temperatures, sea levels, and extreme weather events.",
        ["climate change", "rising temperatures", "extreme weather"]
    ],
    [
        "Advancements in technology have led to the development of AI, machine learning, and data science.",
        ["technology", "AI", "machine learning", "data science"]
    ]
]

# Produce a list of topics covered by the text.
let topics = oracle(text: Str) -> [Str] from topicExamples


# Emotion detection
###################

let EmotionCategories = type {
    happiness!: Num, 
    sadness!: Num,
    fear!: Num, 
    anger!: Num,
    surprise!: Num,
    disgust!: Num
}

# Determine the emotion of a sentence by assigning a value between 0 and 1
# to each category, representing the intensity of each emotion present.
let emotion = oracle(text: Str) -> EmotionCategories


# Coreferences
##############

let corefExamples = [
    [
        "John went to the store. He bought some milk. The store was about to close. Mary was waiting outside. She saw John coming out with his groceries.",
        [
            {
                cluster: ["John", "He", "John", "his"],
                representative: "John"
            },
            {
                cluster: ["the store", "The store"],
                representative: "The store"
            },
            {
                cluster: ["Mary", "She"],
                representative: "Mary"
            }
        ]
    ],
    [
        "Anna loves her dog, Max. She takes him to the park every day. Max enjoys playing with other dogs there.",
        [
            {
                cluster: ["Anna", "She"],
                representative: "Anna"
            },
            {
                cluster: ["her dog, Max", "him", "Max"],
                representative: "her dog, Max"
            },
            {
                cluster: ["the park", "there"],
                representative: "the park"
            }
        ]
    ]
]

let Coreference = type {
    cluster!: [Str],
    representative!: Str
}

# Identify and group all expressions in the text that refer to the same 
# entity, providing a list of clusters with their representative mention.
let coref = oracle(text: Str) -> [Coreference] from corefExamples


# Keyword extraction.
#####################

let keywordsExamples = [
    [
        "Natural language processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language.",
        {
            keywords: ["Natural language processing", "NLP", "artificial intelligence", "interaction", "computers", "humans", "natural language"]
        }
    ],
    [
        "Machine learning algorithms are used to analyze and make predictions from data, allowing for the automation of analytical model building.",
        {
            keywords: ["Machine learning", "algorithms", "analyze", "predictions", "data", "automation", "analytical model building"]
        }
    ],
    [
        "Climate change refers to significant changes in global temperatures and weather patterns over time. Human activities, particularly the burning of fossil fuels, are major contributors to climate change.",
        {
            keywords: ["Climate change", "global temperatures", "weather patterns", "time", "Human activities", "burning of fossil fuels", "contributors"]
        }
    ],
    [
        "Quantum computing leverages the principles of quantum mechanics to perform complex calculations at unprecedented speeds, potentially revolutionizing various fields such as cryptography and materials science.",
        {
            keywords: ["Quantum computing", "quantum mechanics", "complex calculations", "unprecedented speeds", "revolutionizing", "cryptography", "materials science"]
        }
    ],
    [
        "The human brain is an incredibly complex organ, responsible for cognitive functions such as memory, attention, language, and consciousness.",
        {
            keywords: ["human brain", "complex organ", "cognitive functions", "memory", "attention", "language", "consciousness"]
        }
    ]
]

# Extract the most relevant keywords or phrases that summarize the main topics 
# and concepts from the given text.
let keywords = oracle(text: Str) -> {keywords!: [Str]} from keywordsExamples


# Similarity.
#############

let similarityExamples = [
    [
        {
            "text1": "The quick brown fox jumps over the lazy dog.",
            "text2": "A fast, brown fox leaps over a sleeping dog."
        },
        {
            "lexical": 0.6,
            "syntactic": 0.7,
            "semantic": 0.9,
            "pragmatic": 0.8,
            "contextual": 0.5
        }
    ],
    [
        {
            "text1": "Climate change is a pressing global issue that needs immediate attention.",
            "text2": "Global warming is an urgent problem requiring swift action."
        },
        {
            "lexical": 0.4,
            "syntactic": 0.7,
            "semantic": 0.9,
            "pragmatic": 0.8,
            "contextual": 0.7
        }
    ],
    [
        {
            "text1": "How can I reset my password?",
            "text2": "What steps do I need to take to reset my password?"
        },
        {
            "lexical": 0.5,
            "syntactic": 0.8,
            "semantic": 0.9,
            "pragmatic": 0.9,
            "contextual": 0.6
        }
    ],
    [
        {
            "text1": "I love action movies with thrilling plots.",
            "text2": "Can you suggest some exciting action films?"
        },
        {
            "lexical": 0.3,
            "syntactic": 0.6,
            "semantic": 0.8,
            "pragmatic": 0.7,
            "contextual": 0.7
        }
    ],
    [
        {
            "text1": "The service was excellent and the staff were friendly.",
            "text2": "I had a great experience with friendly staff and excellent service."
        },
        {
            "lexical": 0.5,
            "syntactic": 0.7,
            "semantic": 0.9,
            "pragmatic": 0.9,
            "contextual": 0.6
        }
    ],
    [
        {
            "text1": "He went to the store to buy groceries.",
            "text2": "He went to the supermarket to purchase food items."
        },
        {
            "lexical": 0.4,
            "syntactic": 0.6,
            "semantic": 0.8,
            "pragmatic": 0.7,
            "contextual": 0.5
        }
    ],
    [
        {
            "text1": "Advances in artificial intelligence are transforming industries.",
            "text2": "AI developments are revolutionizing various sectors."
        },
        {
            "lexical": 0.5,
            "syntactic": 0.7,
            "semantic": 0.9,
            "pragmatic": 0.8,
            "contextual": 0.7
        }
    ],
    [
        {
            "text1": "Congratulations! You've won a free iPhone. Click here to claim.",
            "text2": "You have been selected for a free prize. Visit this link to get your reward."
        },
        {
            "lexical": 0.4,
            "syntactic": 0.6,
            "semantic": 0.8,
            "pragmatic": 0.9,
            "contextual": 0.6
        }
    ]
]

let Similarity = type {
    lexical!: Num,
    syntactic!: Num,
    semantic!: Num,
    pragmatic!: Num,
    contextual!: Num
}

# Perform a similarity comparison by assigning scores between 0 and 1 for lexical, 
# syntactic, semantic, pragmatic, and contextual similarity between the two given texts.
let similarity = oracle(text1: Str, text2: Str) -> Similarity


# Text Generation.
##################

# Write text that follows the given instruction.
let write = oracle(instruction: Str) -> {result: Str}
