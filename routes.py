from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from flask import current_app as app
from sqlalchemy import desc
from werkzeug.security import check_password_hash
from datetime import datetime

from models import db, User, Category, Tag, Post, Comment, Contact
from forms import LoginForm, PostForm, CategoryForm, TagForm, CommentForm, ContactForm, SearchForm
from utils import generate_slug, get_or_create_tags, search_posts

from functools import wraps

# Create Blueprint for routes
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__, url_prefix='/admin')

# Context processor to add current_year to all templates
@main.context_processor
@admin.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# Authentication decorator for admin routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Main routes

@main.route('/')
def index():
    """Home page showing latest blog posts."""
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    
    posts = Post.query.filter_by(published=True).order_by(
        desc(Post.created_at)).paginate(page=page, per_page=per_page)
    
    categories = Category.query.order_by(Category.name).all()
    tags = Tag.query.order_by(Tag.name).all()
    
    return render_template('index.html', 
                         title='Home',
                         posts=posts,
                         categories=categories,
                         tags=tags)

@main.route('/post/<string:slug>', methods=['GET', 'POST'])
def post(slug):
    """Individual blog post page."""
    post = Post.query.filter_by(slug=slug, published=True).first_or_404()
    
    # Handle comment form
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            name=form.name.data,
            email=form.email.data,
            content=form.content.data,
            post=post
        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been submitted and is awaiting approval.', 'success')
        return redirect(url_for('main.post', slug=post.slug))
    
    # Get approved comments for display
    comments = post.comments.filter_by(approved=True).order_by(Comment.created_at).all()
    
    return render_template('post.html', 
                         title=post.title,
                         post=post,
                         form=form,
                         comments=comments)

@main.route('/category/<string:slug>')
def category(slug):
    """Page showing posts in a specific category."""
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    
    posts = Post.query.filter_by(category=category, published=True).order_by(
        desc(Post.created_at)).paginate(page=page, per_page=per_page)
    
    return render_template('category.html',
                         title=f'Category: {category.name}',
                         category=category,
                         posts=posts)

@main.route('/tag/<string:slug>')
def tag(slug):
    """Page showing posts with a specific tag."""
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = app.config['POSTS_PER_PAGE']
    
    posts = tag.posts.filter_by(published=True).order_by(
        desc(Post.created_at)).paginate(page=page, per_page=per_page)
    
    return render_template('tag.html',
                         title=f'Tag: {tag.name}',
                         tag=tag,
                         posts=posts)

@main.route('/about')
def about():
    """About page."""
    return render_template('about.html', title='About')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with contact form."""
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', title='Contact', form=form)

@main.route('/search')
def search():
    """Search results page."""
    query = request.args.get('query', '')
    if not query:
        return redirect(url_for('main.index'))
    
    posts = search_posts(query)
    
    return render_template('search.html',
                         title='Search Results',
                         query=query,
                         posts=posts)

# Admin routes

@admin.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if 'admin_logged_in' in session:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Authenticate against user in database
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['admin_logged_in'] = True
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html', title='Admin Login', form=form)

@admin.route('/logout')
def logout():
    """Admin logout."""
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

@admin.route('/')
@login_required
def dashboard():
    """Admin dashboard showing blog statistics."""
    post_count = Post.query.count()
    published_post_count = Post.query.filter_by(published=True).count()
    draft_post_count = post_count - published_post_count
    
    category_count = Category.query.count()
    tag_count = Tag.query.count()
    
    comment_count = Comment.query.count()
    pending_comment_count = Comment.query.filter_by(approved=False).count()
    
    contact_count = Contact.query.count()
    unread_contact_count = Contact.query.filter_by(read=False).count()
    
    recent_posts = Post.query.order_by(desc(Post.created_at)).limit(5).all()
    recent_comments = Comment.query.order_by(desc(Comment.created_at)).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         title='Admin Dashboard',
                         post_count=post_count,
                         published_post_count=published_post_count,
                         draft_post_count=draft_post_count,
                         category_count=category_count,
                         tag_count=tag_count,
                         comment_count=comment_count,
                         pending_comment_count=pending_comment_count,
                         contact_count=contact_count,
                         unread_contact_count=unread_contact_count,
                         recent_posts=recent_posts,
                         recent_comments=recent_comments)

@admin.route('/posts')
@login_required
def manage_posts():
    """Admin page for managing blog posts."""
    posts = Post.query.order_by(desc(Post.created_at)).all()
    return render_template('admin/manage_posts.html',
                         title='Manage Posts',
                         posts=posts)

@admin.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Admin page for creating a new blog post."""
    form = PostForm()
    
    if form.validate_on_submit():
        # Process the form data
        title = form.title.data
        slug = form.slug.data if form.slug.data else generate_slug(title)
        
        # Get or create tags
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        tags = get_or_create_tags(tag_names)
        
        # Get the user (using first one for simplicity)
        user = User.query.first()
        if not user:
            # Create a default user if none exists
            user = User(username=app.config['ADMIN_USERNAME'], 
                      email='admin@example.com')
            user.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(user)
            db.session.commit()
        
        # Create the post
        post = Post(
            title=title,
            slug=slug,
            content=form.content.data,
            excerpt=form.excerpt.data,
            published=form.published.data,
            author=user
        )
        
        # Set category if selected
        if form.category_id.data > 0:
            post.category_id = form.category_id.data
            
        # Add tags
        post.tags = tags
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin.manage_posts'))
    
    # Auto-generate slug from title using JavaScript (handled in template)
    return render_template('admin/create_post.html',
                         title='Create Post',
                         form=form)

@admin.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """Admin page for editing an existing blog post."""
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    
    if request.method == 'GET':
        # Pre-populate tags field
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    if form.validate_on_submit():
        # Update slug if needed
        if not form.slug.data:
            form.slug.data = generate_slug(form.title.data)
        
        # Update post object from form
        form.populate_obj(post)
        
        # Handle category
        if form.category_id.data > 0:
            post.category_id = form.category_id.data
        else:
            post.category_id = None
        
        # Update tags
        tag_names = [t.strip() for t in form.tags.data.split(',') if t.strip()]
        tags = get_or_create_tags(tag_names)
        post.tags = tags
        
        db.session.commit()
        
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin.manage_posts'))
    
    return render_template('admin/edit_post.html',
                         title='Edit Post',
                         form=form,
                         post=post)

@admin.route('/posts/delete/<int:id>', methods=['POST'])
@login_required
def delete_post(id):
    """Delete a blog post."""
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin.manage_posts'))

@admin.route('/comments')
@login_required
def manage_comments():
    """Admin page for managing comments."""
    comments = Comment.query.order_by(desc(Comment.created_at)).all()
    return render_template('admin/manage_comments.html',
                         title='Manage Comments',
                         comments=comments)

@admin.route('/comments/approve/<int:id>', methods=['POST'])
@login_required
def approve_comment(id):
    """Approve a comment."""
    comment = Comment.query.get_or_404(id)
    comment.approved = True
    db.session.commit()
    
    flash('Comment approved!', 'success')
    return redirect(url_for('admin.manage_comments'))

@admin.route('/comments/delete/<int:id>', methods=['POST'])
@login_required
def delete_comment(id):
    """Delete a comment."""
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted!', 'success')
    return redirect(url_for('admin.manage_comments'))

@admin.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    """Admin page for managing categories."""
    form = CategoryForm()
    if form.validate_on_submit():
        # Create new category
        category = Category(
            name=form.name.data,
            slug=form.slug.data if form.slug.data else generate_slug(form.name.data)
        )
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin.manage_categories'))
    
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/manage_categories.html',
                         title='Manage Categories',
                         form=form,
                         categories=categories)

@admin.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    """Delete a category."""
    category = Category.query.get_or_404(id)
    
    # Update posts to remove this category
    for post in category.posts:
        post.category_id = None
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted!', 'success')
    return redirect(url_for('admin.manage_categories'))

@admin.route('/tags', methods=['GET', 'POST'])
@login_required
def manage_tags():
    """Admin page for managing tags."""
    form = TagForm()
    if form.validate_on_submit():
        # Create new tag
        tag = Tag(
            name=form.name.data,
            slug=form.slug.data if form.slug.data else generate_slug(form.name.data)
        )
        db.session.add(tag)
        db.session.commit()
        
        flash('Tag created successfully!', 'success')
        return redirect(url_for('admin.manage_tags'))
    
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('admin/manage_tags.html',
                         title='Manage Tags',
                         form=form,
                         tags=tags)

@admin.route('/tags/delete/<int:id>', methods=['POST'])
@login_required
def delete_tag(id):
    """Delete a tag."""
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    
    flash('Tag deleted!', 'success')
    return redirect(url_for('admin.manage_tags'))
