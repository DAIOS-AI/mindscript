################################################################################
# MindScript Language library
# (c) 2024 DAIOS Technologies Ltd.
################################################################################


# Core Text Analysis Functions
# 1. Named Entity Recognition (NER)
# Identify and classify named entities: identify_entities(text)
# 2. Part-of-Speech Tagging (POS)
# Tag parts of speech: tag_pos(text)
# 3. Syntactic Parsing
# Dependency parsing: parse_dependencies(text)
# Constituency parsing: parse_constituents(text)
# 4. Sentiment Analysis
# Analyze sentiment: analyze_sentiment(text)
# 5. Coreference Resolution
# Resolve coreferences: resolve_coreferences(text)
# 6. Text Summarization
# Summarize text: summarize(text)
# 7. Machine Translation
# Translate text: translate(text, target_language)
# 8. Topic Modeling
# Identify topics: model_topics(text)
# 9. Semantic Analysis
# Word sense disambiguation: disambiguate_sense(word, context)
# Semantic role labeling: label_semantic_roles(text)
# 10. Text Similarity and Matching
# Calculate text similarity: calculate_similarity(text1, text2)
# Find similar documents: find_similar_documents(text, document_collection)
# 11. Text Classification
# Classify text: classify(text, model)
# Advanced Functions
# 12. Emotion Detection
# Detect emotions: detect_emotions(text)
# 13. Question Answering
# Answer questions: answer_question(question, context)
# 14. Information Extraction
# Extract structured information: extract_information(text, schema)
# 15. Text Generation
# Generate text: generate_text(prompt, model)

# Named entity reconignition.

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

# Identify and classify various entities such as persons, organizations, locations, 
# dates, products, and concepts within the text.
let ner = oracle(text: Str) -> [{text: Str, entity: Str}] from nerExamples


# PoS - Part of Speech Tagging.

let posExamples = [
    [
        "The quick brown fox jumps over the lazy dog.",
        [
            ["The", "Determiner"],
            ["quick", "Adjective"],
            ["brown", "Adjective"],
            ["fox", "Noun"],
            ["jumps", "Verb"],
            ["over", "Preposition"],
            ["the", "Determiner"],
            ["lazy", "Adjective"],
            ["dog", "Noun"]
        ]
    ],
    [
        "She sells seashells by the seashore.",
        [
            ["She", "Pronoun"],
            ["sells", "Verb"],
            ["seashells", "Noun"],
            ["by", "Preposition"],
            ["the", "Determiner"],
            ["seashore", "Noun"]
        ]
    ],
    [
        "He quickly ran to the store.",
        [
            ["He", "Pronoun"],
            ["quickly", "Adverb"],
            ["ran", "Verb"],
            ["to", "Preposition"],
            ["the", "Determiner"],
            ["store", "Noun"]
        ]
    ],
    [
        "They are planning a big surprise party.",
        [
            ["They", "Pronoun"],
            ["are", "Verb"],
            ["planning", "Verb"],
            ["a", "Determiner"],
            ["big", "Adjective"],
            ["surprise", "Adjective"],
            ["party", "Noun"]
        ]
    ],
    [
        "Reading books can expand your knowledge.",
        [
            ["Reading", "Verb"],
            ["books", "Noun"],
            ["can", "Modal"],
            ["expand", "Verb"],
            ["your", "Pronoun"],
            ["knowledge", "Noun"]
        ]
    ]
]

# Assign a part-of-speech label to each word in a sentence, where each label
# indicates the grammatical category of each word, such as noun, verb, etc.
let tagPOS = oracle(text: Str) -> [[Str]] from posExamples


# Sentiment analysis.

let Sentiment = type {sentiment: Enum(Str, ["negative", "neutral", "positive"])} 

# Determine the sentiment of given text.
let sentiment = oracle(text: Str) -> Sentiment


# Language detection and translation.

# Typical languages.
let languages = ["English", "Mandarin", "Spanish", "Hindi", "German", "Arabic", "French", "Italian"]

# Returns a language detector for the given languages.
let makeLanguageDetector = fun(langs: [Str]?) -> Str -> Str do
    if langs == null do
        langs = languages
    end
    # Detect the language the text is written in.
    oracle(text: Str) -> Enum(Str, langs)
end

# Translate the text into the target language.
let translate = oracle(text: Str, targetLang: Str) -> Str


# Text classification.

# Returns a text classifier for the given categories.
let textClassifier = fun(categories: [Str]) do
    let Categories = type Enum(Str, categories)

    # Classify the text into one of the categories.
    let classifyText = oracle(text: Str) -> Categories
end

# Text summarization.

# Summarize the text.
let summarize = oracle(text: Str) -> Str


# Topic modelling.

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

let test = import("ms/lib/test.ms")

