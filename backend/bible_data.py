"""
Bible metadata: all 66 books with chapter counts, categories, and testament info.
Reading plan definitions and badge criteria.
"""

BIBLE_BOOKS = [
    {"order": 1, "name": "Genesis", "abbr": "Gen", "slug": "genesis", "chapters": 50, "testament": "OT", "category": "Pentateuch"},
    {"order": 2, "name": "Exodus", "abbr": "Exo", "slug": "exodus", "chapters": 40, "testament": "OT", "category": "Pentateuch"},
    {"order": 3, "name": "Leviticus", "abbr": "Lev", "slug": "leviticus", "chapters": 27, "testament": "OT", "category": "Pentateuch"},
    {"order": 4, "name": "Numbers", "abbr": "Num", "slug": "numbers", "chapters": 36, "testament": "OT", "category": "Pentateuch"},
    {"order": 5, "name": "Deuteronomy", "abbr": "Deut", "slug": "deuteronomy", "chapters": 34, "testament": "OT", "category": "Pentateuch"},
    {"order": 6, "name": "Joshua", "abbr": "Josh", "slug": "joshua", "chapters": 24, "testament": "OT", "category": "History"},
    {"order": 7, "name": "Judges", "abbr": "Judg", "slug": "judges", "chapters": 21, "testament": "OT", "category": "History"},
    {"order": 8, "name": "Ruth", "abbr": "Ruth", "slug": "ruth", "chapters": 4, "testament": "OT", "category": "History"},
    {"order": 9, "name": "1 Samuel", "abbr": "1Sam", "slug": "1-samuel", "chapters": 31, "testament": "OT", "category": "History"},
    {"order": 10, "name": "2 Samuel", "abbr": "2Sam", "slug": "2-samuel", "chapters": 24, "testament": "OT", "category": "History"},
    {"order": 11, "name": "1 Kings", "abbr": "1Kgs", "slug": "1-kings", "chapters": 22, "testament": "OT", "category": "History"},
    {"order": 12, "name": "2 Kings", "abbr": "2Kgs", "slug": "2-kings", "chapters": 25, "testament": "OT", "category": "History"},
    {"order": 13, "name": "1 Chronicles", "abbr": "1Chr", "slug": "1-chronicles", "chapters": 29, "testament": "OT", "category": "History"},
    {"order": 14, "name": "2 Chronicles", "abbr": "2Chr", "slug": "2-chronicles", "chapters": 36, "testament": "OT", "category": "History"},
    {"order": 15, "name": "Ezra", "abbr": "Ezra", "slug": "ezra", "chapters": 10, "testament": "OT", "category": "History"},
    {"order": 16, "name": "Nehemiah", "abbr": "Neh", "slug": "nehemiah", "chapters": 13, "testament": "OT", "category": "History"},
    {"order": 17, "name": "Esther", "abbr": "Esth", "slug": "esther", "chapters": 10, "testament": "OT", "category": "History"},
    {"order": 18, "name": "Job", "abbr": "Job", "slug": "job", "chapters": 42, "testament": "OT", "category": "Wisdom"},
    {"order": 19, "name": "Psalms", "abbr": "Psa", "slug": "psalms", "chapters": 150, "testament": "OT", "category": "Wisdom"},
    {"order": 20, "name": "Proverbs", "abbr": "Prov", "slug": "proverbs", "chapters": 31, "testament": "OT", "category": "Wisdom"},
    {"order": 21, "name": "Ecclesiastes", "abbr": "Eccl", "slug": "ecclesiastes", "chapters": 12, "testament": "OT", "category": "Wisdom"},
    {"order": 22, "name": "Song of Solomon", "abbr": "Song", "slug": "song-of-solomon", "chapters": 8, "testament": "OT", "category": "Wisdom"},
    {"order": 23, "name": "Isaiah", "abbr": "Isa", "slug": "isaiah", "chapters": 66, "testament": "OT", "category": "Major Prophets"},
    {"order": 24, "name": "Jeremiah", "abbr": "Jer", "slug": "jeremiah", "chapters": 52, "testament": "OT", "category": "Major Prophets"},
    {"order": 25, "name": "Lamentations", "abbr": "Lam", "slug": "lamentations", "chapters": 5, "testament": "OT", "category": "Major Prophets"},
    {"order": 26, "name": "Ezekiel", "abbr": "Ezek", "slug": "ezekiel", "chapters": 48, "testament": "OT", "category": "Major Prophets"},
    {"order": 27, "name": "Daniel", "abbr": "Dan", "slug": "daniel", "chapters": 12, "testament": "OT", "category": "Major Prophets"},
    {"order": 28, "name": "Hosea", "abbr": "Hos", "slug": "hosea", "chapters": 14, "testament": "OT", "category": "Minor Prophets"},
    {"order": 29, "name": "Joel", "abbr": "Joel", "slug": "joel", "chapters": 3, "testament": "OT", "category": "Minor Prophets"},
    {"order": 30, "name": "Amos", "abbr": "Amos", "slug": "amos", "chapters": 9, "testament": "OT", "category": "Minor Prophets"},
    {"order": 31, "name": "Obadiah", "abbr": "Obad", "slug": "obadiah", "chapters": 1, "testament": "OT", "category": "Minor Prophets"},
    {"order": 32, "name": "Jonah", "abbr": "Jonah", "slug": "jonah", "chapters": 4, "testament": "OT", "category": "Minor Prophets"},
    {"order": 33, "name": "Micah", "abbr": "Mic", "slug": "micah", "chapters": 7, "testament": "OT", "category": "Minor Prophets"},
    {"order": 34, "name": "Nahum", "abbr": "Nah", "slug": "nahum", "chapters": 3, "testament": "OT", "category": "Minor Prophets"},
    {"order": 35, "name": "Habakkuk", "abbr": "Hab", "slug": "habakkuk", "chapters": 3, "testament": "OT", "category": "Minor Prophets"},
    {"order": 36, "name": "Zephaniah", "abbr": "Zeph", "slug": "zephaniah", "chapters": 3, "testament": "OT", "category": "Minor Prophets"},
    {"order": 37, "name": "Haggai", "abbr": "Hag", "slug": "haggai", "chapters": 2, "testament": "OT", "category": "Minor Prophets"},
    {"order": 38, "name": "Zechariah", "abbr": "Zech", "slug": "zechariah", "chapters": 14, "testament": "OT", "category": "Minor Prophets"},
    {"order": 39, "name": "Malachi", "abbr": "Mal", "slug": "malachi", "chapters": 4, "testament": "OT", "category": "Minor Prophets"},
    {"order": 40, "name": "Matthew", "abbr": "Matt", "slug": "matthew", "chapters": 28, "testament": "NT", "category": "Gospels"},
    {"order": 41, "name": "Mark", "abbr": "Mark", "slug": "mark", "chapters": 16, "testament": "NT", "category": "Gospels"},
    {"order": 42, "name": "Luke", "abbr": "Luke", "slug": "luke", "chapters": 24, "testament": "NT", "category": "Gospels"},
    {"order": 43, "name": "John", "abbr": "John", "slug": "john", "chapters": 21, "testament": "NT", "category": "Gospels"},
    {"order": 44, "name": "Acts", "abbr": "Acts", "slug": "acts", "chapters": 28, "testament": "NT", "category": "History"},
    {"order": 45, "name": "Romans", "abbr": "Rom", "slug": "romans", "chapters": 16, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 46, "name": "1 Corinthians", "abbr": "1Cor", "slug": "1-corinthians", "chapters": 16, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 47, "name": "2 Corinthians", "abbr": "2Cor", "slug": "2-corinthians", "chapters": 13, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 48, "name": "Galatians", "abbr": "Gal", "slug": "galatians", "chapters": 6, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 49, "name": "Ephesians", "abbr": "Eph", "slug": "ephesians", "chapters": 6, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 50, "name": "Philippians", "abbr": "Phil", "slug": "philippians", "chapters": 4, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 51, "name": "Colossians", "abbr": "Col", "slug": "colossians", "chapters": 4, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 52, "name": "1 Thessalonians", "abbr": "1Thes", "slug": "1-thessalonians", "chapters": 5, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 53, "name": "2 Thessalonians", "abbr": "2Thes", "slug": "2-thessalonians", "chapters": 3, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 54, "name": "1 Timothy", "abbr": "1Tim", "slug": "1-timothy", "chapters": 6, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 55, "name": "2 Timothy", "abbr": "2Tim", "slug": "2-timothy", "chapters": 4, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 56, "name": "Titus", "abbr": "Titus", "slug": "titus", "chapters": 3, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 57, "name": "Philemon", "abbr": "Phlm", "slug": "philemon", "chapters": 1, "testament": "NT", "category": "Pauline Epistles"},
    {"order": 58, "name": "Hebrews", "abbr": "Heb", "slug": "hebrews", "chapters": 13, "testament": "NT", "category": "General Epistles"},
    {"order": 59, "name": "James", "abbr": "Jas", "slug": "james", "chapters": 5, "testament": "NT", "category": "General Epistles"},
    {"order": 60, "name": "1 Peter", "abbr": "1Pet", "slug": "1-peter", "chapters": 5, "testament": "NT", "category": "General Epistles"},
    {"order": 61, "name": "2 Peter", "abbr": "2Pet", "slug": "2-peter", "chapters": 3, "testament": "NT", "category": "General Epistles"},
    {"order": 62, "name": "1 John", "abbr": "1Jn", "slug": "1-john", "chapters": 5, "testament": "NT", "category": "General Epistles"},
    {"order": 63, "name": "2 John", "abbr": "2Jn", "slug": "2-john", "chapters": 1, "testament": "NT", "category": "General Epistles"},
    {"order": 64, "name": "3 John", "abbr": "3Jn", "slug": "3-john", "chapters": 1, "testament": "NT", "category": "General Epistles"},
    {"order": 65, "name": "Jude", "abbr": "Jude", "slug": "jude", "chapters": 1, "testament": "NT", "category": "General Epistles"},
    {"order": 66, "name": "Revelation", "abbr": "Rev", "slug": "revelation", "chapters": 22, "testament": "NT", "category": "Prophecy"},
]

TOTAL_CHAPTERS = sum(b["chapters"] for b in BIBLE_BOOKS)  # 1189
NT_BOOKS = [b for b in BIBLE_BOOKS if b["testament"] == "NT"]
OT_BOOKS = [b for b in BIBLE_BOOKS if b["testament"] == "OT"]
NT_CHAPTERS = sum(b["chapters"] for b in NT_BOOKS)  # 260

CATEGORIES = {
    "Pentateuch": {"icon": "scroll", "description": "The Law - Genesis through Deuteronomy"},
    "History": {"icon": "landmark", "description": "Historical Books"},
    "Wisdom": {"icon": "brain", "description": "Poetry & Wisdom Literature"},
    "Major Prophets": {"icon": "megaphone", "description": "Isaiah through Daniel"},
    "Minor Prophets": {"icon": "message-circle", "description": "Hosea through Malachi"},
    "Gospels": {"icon": "heart", "description": "The Life of Christ"},
    "Pauline Epistles": {"icon": "mail", "description": "Letters of Paul"},
    "General Epistles": {"icon": "book-open", "description": "Hebrews through Jude"},
    "Prophecy": {"icon": "eye", "description": "Revelation"},
}

def get_all_chapters(books=None):
    """Return flat list of (book_slug, book_name, chapter_num) for given books."""
    if books is None:
        books = BIBLE_BOOKS
    chapters = []
    for b in books:
        for ch in range(1, b["chapters"] + 1):
            chapters.append({"book_slug": b["slug"], "book_name": b["name"], "chapter": ch})
    return chapters

READING_PLANS = [
    {
        "id": "whole-bible-1yr",
        "name": "Whole Bible in 1 Year",
        "description": "Read through the entire Bible from Genesis to Revelation in 365 days.",
        "duration_days": 365,
        "icon": "book",
        "color": "#D97757",
        "books": "all",
    },
    {
        "id": "nt-90-days",
        "name": "New Testament in 90 Days",
        "description": "Read the complete New Testament in just 90 days.",
        "duration_days": 90,
        "icon": "zap",
        "color": "#E8A365",
        "books": "nt",
    },
    {
        "id": "wisdom-books",
        "name": "Wisdom Books",
        "description": "Dive deep into Job, Psalms, Proverbs, Ecclesiastes & Song of Solomon.",
        "duration_days": 90,
        "icon": "lightbulb",
        "color": "#8BA888",
        "books": "wisdom",
    },
    {
        "id": "life-of-david",
        "name": "The Life of David",
        "description": "Follow David's journey through 1 & 2 Samuel, selected Psalms, and 1 Chronicles.",
        "duration_days": 60,
        "icon": "crown",
        "color": "#7B8EC4",
        "books": "david",
    },
    {
        "id": "gospels-30",
        "name": "The Four Gospels",
        "description": "Read all four Gospel accounts in 30 days.",
        "duration_days": 30,
        "icon": "heart",
        "color": "#C47B7B",
        "books": "gospels",
    },
]

DAVID_BOOKS = ["1-samuel", "2-samuel", "1-chronicles"]
DAVID_PSALMS = list(range(1, 42)) + [51, 52, 54, 56, 57, 59, 60, 63, 142]

def get_plan_chapters(plan_id):
    """Generate chapter list for a reading plan."""
    plan = next((p for p in READING_PLANS if p["id"] == plan_id), None)
    if not plan:
        return []
    
    if plan["books"] == "all":
        return get_all_chapters()
    elif plan["books"] == "nt":
        return get_all_chapters(NT_BOOKS)
    elif plan["books"] == "wisdom":
        wisdom_books = [b for b in BIBLE_BOOKS if b["category"] == "Wisdom"]
        return get_all_chapters(wisdom_books)
    elif plan["books"] == "david":
        chapters = []
        for b in BIBLE_BOOKS:
            if b["slug"] in DAVID_BOOKS:
                for ch in range(1, b["chapters"] + 1):
                    chapters.append({"book_slug": b["slug"], "book_name": b["name"], "chapter": ch})
        # Add specific Psalms
        for ps in DAVID_PSALMS:
            if ps <= 150:
                chapters.append({"book_slug": "psalms", "book_name": "Psalms", "chapter": ps})
        return chapters
    elif plan["books"] == "gospels":
        gospel_books = [b for b in BIBLE_BOOKS if b["category"] == "Gospels"]
        return get_all_chapters(gospel_books)
    return []

BADGES = [
    {"id": "pentateuch", "name": "The Pentateuch", "description": "Completed Genesis through Deuteronomy", "icon": "scroll", "category": "Pentateuch", "color": "#D97757"},
    {"id": "history-ot", "name": "History Buff", "description": "Completed all OT Historical Books", "icon": "landmark", "category": "History", "color": "#7B8EC4"},
    {"id": "wisdom", "name": "The Wisdom Books", "description": "Completed Job through Song of Solomon", "icon": "brain", "category": "Wisdom", "color": "#E8A365"},
    {"id": "major-prophets", "name": "Major Prophets", "description": "Completed Isaiah through Daniel", "icon": "megaphone", "category": "Major Prophets", "color": "#8BA888"},
    {"id": "minor-prophets", "name": "Minor Prophets", "description": "Completed Hosea through Malachi", "icon": "message-circle", "category": "Minor Prophets", "color": "#C47B7B"},
    {"id": "gospels", "name": "Gospel Reader", "description": "Completed all four Gospels", "icon": "heart", "category": "Gospels", "color": "#D97757"},
    {"id": "pauline", "name": "Pauline Epistles", "description": "Completed Romans through Philemon", "icon": "mail", "category": "Pauline Epistles", "color": "#7B8EC4"},
    {"id": "general-epistles", "name": "General Epistles", "description": "Completed Hebrews through Jude", "icon": "book-open", "category": "General Epistles", "color": "#E8A365"},
    {"id": "nt-complete", "name": "New Testament", "description": "Completed the entire New Testament", "icon": "star", "category": "all_nt", "color": "#8BA888"},
    {"id": "whole-bible", "name": "Whole Bible", "description": "Completed the entire Bible!", "icon": "award", "category": "all", "color": "#D97757"},
    {"id": "streak-7", "name": "Week Warrior", "description": "7-day reading streak", "icon": "flame", "category": "streak", "color": "#E8A365"},
    {"id": "streak-30", "name": "Monthly Master", "description": "30-day reading streak", "icon": "flame", "category": "streak", "color": "#D97757"},
    {"id": "streak-100", "name": "Century Reader", "description": "100-day reading streak", "icon": "flame", "category": "streak", "color": "#C47B7B"},
]

MOOD_SUGGESTIONS = {
    "anxious": {
        "label": "Anxious",
        "icon": "cloud-rain",
        "color": "#7B8EC4",
        "passages": [
            {"ref": "Psalms 23", "book_slug": "psalms", "chapter": 23, "title": "The Lord is my Shepherd"},
            {"ref": "Psalms 46", "book_slug": "psalms", "chapter": 46, "title": "God is our refuge and strength"},
            {"ref": "Philippians 4", "book_slug": "philippians", "chapter": 4, "title": "Do not be anxious about anything"},
            {"ref": "Matthew 6", "book_slug": "matthew", "chapter": 6, "title": "Do not worry about tomorrow"},
            {"ref": "Isaiah 41", "book_slug": "isaiah", "chapter": 41, "title": "Fear not, for I am with you"},
        ]
    },
    "joyful": {
        "label": "Joyful",
        "icon": "sun",
        "color": "#E8A365",
        "passages": [
            {"ref": "Psalms 100", "book_slug": "psalms", "chapter": 100, "title": "Make a joyful noise"},
            {"ref": "Psalms 150", "book_slug": "psalms", "chapter": 150, "title": "Praise the Lord!"},
            {"ref": "Philippians 1", "book_slug": "philippians", "chapter": 1, "title": "Rejoice in the Lord always"},
            {"ref": "James 1", "book_slug": "james", "chapter": 1, "title": "Count it all joy"},
            {"ref": "Psalms 16", "book_slug": "psalms", "chapter": 16, "title": "Fullness of joy in Your presence"},
        ]
    },
    "grieving": {
        "label": "Grieving",
        "icon": "heart",
        "color": "#C47B7B",
        "passages": [
            {"ref": "Psalms 34", "book_slug": "psalms", "chapter": 34, "title": "The Lord is near to the brokenhearted"},
            {"ref": "Revelation 21", "book_slug": "revelation", "chapter": 21, "title": "He will wipe away every tear"},
            {"ref": "2 Corinthians 1", "book_slug": "2-corinthians", "chapter": 1, "title": "The God of all comfort"},
            {"ref": "Psalms 42", "book_slug": "psalms", "chapter": 42, "title": "Why are you cast down, O my soul?"},
            {"ref": "John 14", "book_slug": "john", "chapter": 14, "title": "Let not your hearts be troubled"},
        ]
    },
    "grateful": {
        "label": "Grateful",
        "icon": "gift",
        "color": "#8BA888",
        "passages": [
            {"ref": "Psalms 103", "book_slug": "psalms", "chapter": 103, "title": "Bless the Lord, O my soul"},
            {"ref": "1 Thessalonians 5", "book_slug": "1-thessalonians", "chapter": 5, "title": "Give thanks in all circumstances"},
            {"ref": "Colossians 3", "book_slug": "colossians", "chapter": 3, "title": "And be thankful"},
            {"ref": "Psalms 136", "book_slug": "psalms", "chapter": 136, "title": "His steadfast love endures forever"},
            {"ref": "Psalms 107", "book_slug": "psalms", "chapter": 107, "title": "Give thanks to the Lord"},
        ]
    },
    "seeking": {
        "label": "Seeking Direction",
        "icon": "compass",
        "color": "#D97757",
        "passages": [
            {"ref": "Proverbs 3", "book_slug": "proverbs", "chapter": 3, "title": "Trust in the Lord with all your heart"},
            {"ref": "Psalms 119", "book_slug": "psalms", "chapter": 119, "title": "Your word is a lamp to my feet"},
            {"ref": "James 1", "book_slug": "james", "chapter": 1, "title": "If any of you lacks wisdom"},
            {"ref": "Isaiah 30", "book_slug": "isaiah", "chapter": 30, "title": "This is the way, walk in it"},
            {"ref": "Romans 12", "book_slug": "romans", "chapter": 12, "title": "Be transformed by the renewal of your mind"},
        ]
    },
    "lonely": {
        "label": "Lonely",
        "icon": "users",
        "color": "#A39A94",
        "passages": [
            {"ref": "Psalms 139", "book_slug": "psalms", "chapter": 139, "title": "You are never alone"},
            {"ref": "Deuteronomy 31", "book_slug": "deuteronomy", "chapter": 31, "title": "He will never leave you"},
            {"ref": "Hebrews 13", "book_slug": "hebrews", "chapter": 13, "title": "I will never forsake you"},
            {"ref": "Psalms 27", "book_slug": "psalms", "chapter": 27, "title": "The Lord is my light"},
            {"ref": "Isaiah 43", "book_slug": "isaiah", "chapter": 43, "title": "When you pass through the waters"},
        ]
    },
}

DAILY_VERSES = [
    {"ref": "John 3:16", "text": "For God so loved the world, that He gave His only begotten Son, that everyone who believes into Him would not perish, but would have eternal life."},
    {"ref": "Philippians 4:13", "text": "I am able to do all things in Him who empowers me."},
    {"ref": "Psalm 23:1", "text": "Jehovah is my Shepherd; I will lack nothing."},
    {"ref": "Romans 8:28", "text": "And we know that all things work together for good to those who love God, to those who are called according to His purpose."},
    {"ref": "Jeremiah 29:11", "text": "For I know the thoughts that I think about you, declares Jehovah, thoughts of peace and not of evil, to give you a future and a hope."},
    {"ref": "Proverbs 3:5-6", "text": "Trust in Jehovah with all your heart, and do not lean on your own understanding; In all your ways acknowledge Him, and He will make your paths straight."},
    {"ref": "Isaiah 40:31", "text": "Yet those who wait on Jehovah will renew their strength; they will mount up with wings like eagles; they will run and not faint; they will walk and not become weary."},
    {"ref": "Psalm 46:10", "text": "Be still and know that I am God. I will be exalted among the nations; I will be exalted on the earth."},
    {"ref": "Matthew 11:28", "text": "Come to Me all who toil and are burdened, and I will give you rest."},
    {"ref": "2 Timothy 1:7", "text": "For God has not given us a spirit of cowardice, but of power and of love and of sobermindedness."},
    {"ref": "Psalm 119:105", "text": "Your word is a lamp to my feet and a light to my path."},
    {"ref": "Romans 12:2", "text": "And do not be fashioned according to this age, but be transformed by the renewing of the mind that you may prove what the will of God is, that which is good and well pleasing and perfect."},
    {"ref": "Hebrews 11:1", "text": "Now faith is the substantiation of things hoped for, the conviction of things not seen."},
    {"ref": "Galatians 2:20", "text": "I am crucified with Christ; and it is no longer I who live, but it is Christ who lives in me; and the life which I now live in the flesh I live in faith, the faith of the Son of God, who loved me and gave Himself up for me."},
    {"ref": "1 John 4:19", "text": "We love because He first loved us."},
    {"ref": "Psalm 27:1", "text": "Jehovah is my light and my salvation; whom shall I fear? Jehovah is the strength of my life; of whom shall I be afraid?"},
    {"ref": "Ephesians 2:8-9", "text": "For by grace you have been saved through faith, and this not of yourselves; it is the gift of God; not of works that no one should boast."},
    {"ref": "Matthew 6:33", "text": "But seek first His kingdom and His righteousness, and all these things will be added to you."},
    {"ref": "Colossians 3:23", "text": "Whatever you do, work from the soul as to the Lord and not to men."},
    {"ref": "Psalm 37:4", "text": "Delight yourself in Jehovah, and He will give you the desires of your heart."},
    {"ref": "Joshua 1:9", "text": "Have I not commanded you? Be strong and take courage; do not be afraid or dismayed. For Jehovah your God is with you wherever you go."},
    {"ref": "Lamentations 3:22-23", "text": "It is Jehovah's lovingkindness that we are not consumed, for His compassions do not fail; they are new every morning; great is Your faithfulness."},
    {"ref": "1 Corinthians 10:13", "text": "No temptation has taken you except that which is common to man; and God is faithful, who will not allow you to be tempted beyond what you are able."},
    {"ref": "2 Corinthians 5:17", "text": "So then if anyone is in Christ, he is a new creation. The old things have passed away; behold, they have become new."},
    {"ref": "Philippians 4:6-7", "text": "In nothing be anxious, but in everything, by prayer and petition with thanksgiving, let your requests be made known to God; and the peace of God, which surpasses every man's understanding, will guard your hearts and your thoughts in Christ Jesus."},
    {"ref": "Psalm 91:1-2", "text": "He who dwells in the secret place of the Most High will abide in the shadow of the Almighty. I will say of Jehovah, My refuge and my fortress; my God, in whom I trust."},
    {"ref": "Isaiah 41:10", "text": "Do not fear, for I am with you; do not be anxious, for I am your God. I will strengthen you; surely I will help you; surely I will uphold you with the right hand of My righteousness."},
    {"ref": "Romans 15:13", "text": "Now the God of hope fill you with all joy and peace in believing, that you may abound in hope in the power of the Holy Spirit."},
    {"ref": "Psalm 34:8", "text": "Taste and see that Jehovah is good. Blessed is the man who takes refuge in Him."},
    {"ref": "John 14:27", "text": "Peace I leave with you; My peace I give to you; not as the world gives do I give to you. Do not let your heart be troubled, neither let it be afraid."},
    {"ref": "Psalm 145:18", "text": "Jehovah is near to all who call upon Him, to all who call upon Him in truth."},
]
