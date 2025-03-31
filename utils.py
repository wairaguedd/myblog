import re
from unidecode import unidecode
from sqlalchemy import or_
from models import Post, Tag

def generate_slug(text):
    """
    Generate a URL-friendly slug from the given text.
    
    Args:
        text (str): The text to convert to a slug
        
    Returns:
        str: A URL-friendly slug
    """
    # Convert to lowercase and normalize unicode characters
    text = unidecode(text.lower())
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Replace multiple hyphens with a single hyphen
    slug = re.sub(r'-+', '-', slug)
    return slug

def get_or_create_tags(tag_names):
    """
    Get or create tags from a list of tag names.
    
    Args:
        tag_names (list): List of tag names
        
    Returns:
        list: List of Tag objects
    """
    from models import db, Tag
    
    tags = []
    for name in tag_names:
        name = name.strip()
        if not name:
            continue
            
        # Look for existing tag
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            # Create new tag if it doesn't exist
            slug = generate_slug(name)
            tag = Tag(name=name, slug=slug)
            db.session.add(tag)
            
        tags.append(tag)
        
    return tags

def search_posts(query, published_only=True):
    """
    Search for posts matching the query string.
    
    Args:
        query (str): The search query
        published_only (bool): Whether to only return published posts
        
    Returns:
        list: List of Post objects matching the query
    """
    search_term = f"%{query}%"
    
    post_query = Post.query.filter(
        or_(
            Post.title.ilike(search_term),
            Post.content.ilike(search_term),
            Post.excerpt.ilike(search_term)
        )
    )
    
    if published_only:
        post_query = post_query.filter_by(published=True)
        
    return post_query.order_by(Post.created_at.desc()).all()
