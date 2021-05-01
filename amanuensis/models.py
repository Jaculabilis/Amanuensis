from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy.orm import relationship

from .database import ModelBase


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
    last_login = Column(DateTime, nullable=True)

    # The timestamp the user last performed an action
    last_activity = Column(DateTime, nullable=True)

    #############################
    # Foreign key relationships #
    #############################

    memberships = relationship('Membership', back_populates='player')


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

    # Optional title override, instead of "Lexicon <name>"
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
    started = Column(DateTime, nullable=True)

    # The timestamp when the last turn was published
    completed = Column(DateTime, nullable=True)

    ##############
    # Turn state #
    ##############

    # The current turn number
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
    join_password = Column(String, nullable=True)

    # Maximum number of players who can join
    player_limit = Column(Integer, nullable=True)

    # Maximum number of characters per player
    character_limit = Column(Integer, nullable=True, default=1)

    ####################
    # Publish settings #
    ####################

    # Recurrence for turn publish attempts, as crontab spec
    publish_recur = Column(String, nullable=True)

    # Whether to attempt publish when an article is approved
    publish_asap = Column(Boolean, nullable=False, default=True)

    # Allow an incomplete turn to be published with this many articles
    publish_quorum = Column(Integer, nullable=True)

    #####################
    # Addendum settings #
    #####################

    # Whether to allow addendum articles
    allow_addendum = Column(Boolean, nullable=False, default=False)

    # Maximum number of addenda per player per turn
    addendum_turn_limit = Column(Integer, nullable=True)

    # Maximum number of addenda per title
    addendum_title_limit = Column(Integer, nullable=True)

    #################
    # Peer settings #
    #################

    # Enable the social posting feature
    allow_post = Column(Boolean, nullable=False, default=True)

    # Show title stubs in the index when a new article is approved
    show_stubs = Column(Boolean, nullable=False, default=False)

    #############################
    # Foreign key relationships #
    #############################

    memberships = relationship('Membership', back_populates='lexicon')


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
