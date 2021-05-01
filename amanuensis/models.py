import enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.orm import relationship, backref
from uuid import uuid4

from .database import ModelBase, Uuid


class User(ModelBase):
    """
    Represents a single user of Amanuensis.
    """
    __tablename__ = 'user'

    #############
    # User info #
    #############

    # Primary user id
    id = Column(Integer, primary_key=True)

    # The user's human-readable identifier
    username = Column(String, nullable=False, unique=True)

    # Hashed and salted password
    password = Column(String, nullable=False)

    # Human-readable username as shown to other users
    display_name = Column(String, nullable=False)

    # Whether the user can access site admin functions
    is_site_admin = Column(Boolean, nullable=False, server_default=text('FALSE'))

    ####################
    # History tracking #
    ####################

    # The timestamp the user was created
    created = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # The timestamp the user last logged in
    # This is NULL if the user has never logged in
    last_login = Column(DateTime, nullable=True)

    # The timestamp the user last performed an action
    # This is NULL if the user has never performed an action
    last_activity = Column(DateTime, nullable=True)

    #############################
    # Foreign key relationships #
    #############################

    memberships = relationship('Membership', back_populates='user')
    characters = relationship('Character', back_populates='user')
    articles = relationship('Article', back_populates='user')


class Lexicon(ModelBase):
    """
    Represents a single game of Lexicon.
    """
    __tablename__ = 'lexicon'

    #############
    # Game info #
    #############

    # Primary lexicon id
    id = Column(Integer, primary_key=True)

    # The lexicon's human-readable identifier
    name = Column(String, nullable=False, unique=True)

    # Optional title override
    # If this is NULL, the title is rendered as "Lexicon <name>"
    title = Column(String, nullable=True)

    # The initial prompt describing the game's setting
    prompt = Column(String, nullable=False, default="")

    ####################
    # History tracking #
    ####################

    # The timestamp the lexicon was created
    created = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # The timestamp of the last change in game state
    last_updated = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # The timestamp the first turn was started
    # This is NULL until the game starts
    started = Column(DateTime, nullable=True)

    # The timestamp when the last turn was published
    # This is NULL until the game is completed
    completed = Column(DateTime, nullable=True)

    ##############
    # Turn state #
    ##############

    # The current turn number
    # This is NULL until the game strts
    current_turn = Column(Integer, nullable=True)

    # The number of turns in the game
    turn_count = Column(Integer, nullable=False)

    ################################
    # Visibility and join settings #
    ################################

    # Whether players can join the game
    joinable = Column(Boolean, nullable=False, default=False)

    # Whether the game is listed on public pages
    public = Column(Boolean, nullable=False, default=False)

    # Optional password required to join
    # If this is NULL, no password is required to join
    join_password = Column(String, nullable=True)

    # Maximum number of players who can join
    # If this is NULL, there is no limit to player joins
    player_limit = Column(Integer, nullable=True)

    # Maximum number of characters per player
    # If this is NULL, there is no limit to creating characters
    character_limit = Column(Integer, nullable=True, default=1)

    ####################
    # Publish settings #
    ####################

    # Recurrence for turn publish attempts, as crontab spec
    # If this is NULL, turns will not publish on a recurrence
    publish_recur = Column(String, nullable=True)

    # Whether to attempt publish when an article is approved
    publish_asap = Column(Boolean, nullable=False, default=True)

    # Allow an incomplete turn to be published with this many articles
    # If this is NULL, the publish quorum is the number of characters
    publish_quorum = Column(Integer, nullable=True)

    #####################
    # Addendum settings #
    #####################

    # Whether to allow addendum articles
    allow_addendum = Column(Boolean, nullable=False, default=False)

    # Maximum number of addenda per player per turn
    # If this is NULL, there is no limit
    addendum_turn_limit = Column(Integer, nullable=True)

    # Maximum number of addenda per title
    # If this is NULL, there is no limit
    addendum_title_limit = Column(Integer, nullable=True)

    ##########################
    # Collaboration settings #
    ##########################

    # Enable the social posting feature
    allow_post = Column(Boolean, nullable=False, default=True)

    # Show title stubs in the index when a new article is approved
    show_stubs = Column(Boolean, nullable=False, default=True)

    # Show other players' progress for the current turn
    show_peer_progress = Column(Boolean, nullable=False, default=True)

    #############################
    # Foreign key relationships #
    #############################

    memberships = relationship('Membership', back_populates='lexicon')
    characters = relationship('Character', back_populates='lexicon')
    articles = relationship('Article', back_populates='lexicon')
    indexes = relationship('ArticleIndex', back_populates='lexicon')
    index_rules = relationship('ArticleIndexRule', back_populates='lexicon')


class Membership(ModelBase):
    """
    Represents a user's participation in a Lexicon game.
    """
    __tablename__ = 'membership'

    ###################
    # Membership keys #
    ###################

    # Primary membership id
    id = Column(Integer, primary_key=True)

    # The user who is a member of a lexicon
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # The lexicon of which the user is a member
    lexicon_id = Column(Integer, ForeignKey('lexicon.id'), nullable=False)

    ####################
    # History tracking #
    ####################

    # Timestamp the user joined the game
    joined = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    ###################
    # Player settings #
    ###################

    # Whether the user can access editor functions
    is_editor = Column(Boolean, nullable=False, server_default=text('FALSE'))

    #########################
    # Notification settings #
    #########################

    # Whether the user should be notified when an article becomes reviewable
    notify_ready = Column(Boolean, nullable=False, default=True)

    # Whether the user should be notified when one of their articles is rejected
    notify_reject = Column(Boolean, nullable=False, default=True)

    # Whether the user should be notified when one of their articles is approved
    notify_approve = Column(Boolean, nullable=False, default=True)

    #############################
    # Foreign key relationships #
    #############################

    user = relationship('User', back_populates='memberships')
    lexicon = relationship('Lexicon', back_populates='memberships')


class Character(ModelBase):
    """
    Represents a character played by a uaser in a Lexicon game.
    """
    __tablename__ = 'character'

    ##################
    # Character info #
    ##################

    # Primary character id
    id = Column(Integer, primary_key=True)

    # Public-facing character id
    public_id = Column(Uuid, nullable=False, unique=True, default=uuid4)

    # The lexicon to which this character belongs
    lexicon_id = Column(Integer, ForeignKey('lexicon.id'), nullable=False)

    # The user to whom this character belongs
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # The character's name
    name = Column(String, nullable=False)

    # The character's signature
    signature = Column(String, nullable=False)

    #############################
    # Foreign key relationships #
    #############################

    user = relationship('User', back_populates='characters')
    lexicon = relationship('Lexicon', back_populates='characters')
    articles = relationship('Article', back_populates='character')
    index_rules = relationship('ArticleIndexRule', back_populates='character')


class ArticleState(enum.Enum):
    """
    The step of the editorial process an article is in.
    """
    DRAFT = 0
    SUBMITTED = 1
    APPROVED = 2


class Article(ModelBase):
    """
    Represents a single article in a lexicon.
    """
    __tablename__ = 'article'

    ################
    # Article info #
    ################

    # Primary article id
    id = Column(Integer, primary_key=True)

    # Public-facing article id
    public_id = Column(Uuid, nullable=False, unique=True, default=uuid4)

    # The lexicon to which this article belongs
    lexicon_id = Column(Integer, ForeignKey('lexicon.id'), nullable=False)

    # The character who is the author of this article
    # If this is NULL, the article is written by Ersatz Scrivener
    character_id = Column(Integer, ForeignKey('character.id'), nullable=True)

    # The user who owns this article
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # The article to which this is an addendum
    addendum_to = Column(Integer, ForeignKey('article.id'), nullable=True)

    #################
    # Article state #
    #################

    # The turn in which the article was published
    # This is NULL until the article is published
    turn = Column(Integer, nullable=True)

    # The stage of review the article is in
    state = Column(Enum(ArticleState), nullable=False, default=ArticleState.DRAFT)

    # The number of times the article has been submitted
    submit_nonce = Column(Integer, nullable=False, default=0)

    ####################
    # History tracking #
    ####################

    # Timestamp the content of the article was last updated
    last_updated = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    # Timestamp the article was last submitted
    # This is NULL until the article is submitted
    submitted = Column(DateTime, nullable=True)

    # Timestamp the article was last approved
    # This is NULL until the article is approved
    approved = Column(DateTime, nullable=True)

    ###################
    # Article content #
    ###################

    # The article's title
    title = Column(String, nullable=False, default="")

    # The article's text
    body = Column(Text, nullable=False)

    #############################
    # Foreign key relationships #
    #############################

    lexicon = relationship('Lexicon', back_populates='articles')
    character = relationship('Character', back_populates='articles')
    user = relationship('User', back_populates='articles')
    addenda = relationship('Article', backref=backref('parent', remote_side=[id]))


class IndexType(enum.Enum):
    """
    The title-matching behavior of an article index.
    """
    CHAR = 0
    RANGE = 1
    PREFIX = 2
    ETC = 3


class ArticleIndex(ModelBase):
    """
    Represents an index definition.
    """
    __tablename__ = 'article_index'

    ##############
    # Index info #
    ##############

    # Primary index id
    id = Column(Integer, primary_key=True)

    # The lexicon this index is in
    lexicon_id = Column(Integer, ForeignKey('lexicon.id'), nullable=False)

    # The index type
    index_type = Column(Enum(IndexType), nullable=False)

    # The index pattern
    pattern = Column(String, nullable=False)

    # The order in which the index is processed
    logical_order = Column(Integer, nullable=False, default=0)

    # The order in which the index is displayed
    display_order = Column(Integer, nullable=False, default=0)

    # The maximum number of articles allowed in this index
    # If this is NULL, there is no limit on this index
    capacity = Column(Integer, nullable=True)

    #############################
    # Foreign key relationships #
    #############################

    lexicon = relationship('Lexicon', back_populates='indexes')
    index_rules = relationship('ArticleIndexRule', back_populates='index')


class ArticleIndexRule(ModelBase):
    """
    Represents a restriction of which index a character may write in for a turn.
    A character with multiple index rules may write in any index that satisfies
    a rule. A character with no index rules may write in any index.
    """
    __tablename__ = 'article_index_rule'

    ###################
    # Index rule info #
    ###################

    # Primary index rule id
    id = Column(Integer, primary_key=True)

    # The lexicon of this index rule
    lexicon_id = Column(Integer, ForeignKey('lexicon.id'), nullable=False)

    # The character to whom this rule applies
    character_id = Column(Integer, ForeignKey('character.id'), nullable=False)

    # The index to which the character is restricted
    index = Column(Integer, ForeignKey('index.id'), nullable=False)

    # The turn in which this rule applies
    turn = Column(Integer, nullable=False)

    #############################
    # Foreign key relationships #
    #############################

    lexicon = relationship('Lexicon', back_populates='index_rules')
    index = relationship('ArticleIndex', back_populates='index_rules')
    character = relationship('Character', back_populates='index_rules')
