"""Command-line interface for Naukri Scraper."""
import os
import click
from datetime import datetime
from dotenv import load_dotenv

from naukri_scraper import NaukriEmployerScraper
from data_manager import DataManager
from ai_integration import AIIntegration
from models import init_db

# Load environment variables
load_dotenv()


@click.group()
def cli():
    """Naukri Employer Automation Utility - Search and manage candidate profiles."""
    pass


@cli.command()
def init():
    """Initialize the database."""
    try:
        init_db()
        click.echo("✓ Database initialized successfully!")
    except Exception as e:
        click.echo(f"✗ Error initializing database: {e}", err=True)


@cli.command()
@click.option('--username', prompt=True, help='Naukri employer username/email')
@click.option('--password', prompt=True, hide_input=True, help='Naukri employer password')
@click.option('--job-role', prompt=True, help='Job role/title to search')
@click.option('--exp-min', type=float, help='Minimum years of experience')
@click.option('--exp-max', type=float, help='Maximum years of experience')
@click.option('--location', help='Job location')
@click.option('--job-type', help='Job type (Full-time, Contract, etc.)')
@click.option('--max-results', default=50, help='Maximum number of results')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
def search(username, password, job_role, exp_min, exp_max, location, job_type, max_results, headless):
    """Search for candidates on Naukri."""
    try:
        click.echo(f"Searching for: {job_role}")
        
        # Create data manager
        dm = DataManager()
        
        # Create job search record
        job_search = dm.create_job_search(
            job_role=job_role,
            experience_min=exp_min,
            experience_max=exp_max,
            location=location,
            job_type=job_type
        )
        click.echo(f"✓ Created job search record (ID: {job_search.id})")
        
        # Initialize scraper
        with NaukriEmployerScraper(username, password, headless=headless) as scraper:
            click.echo("Logging in to Naukri...")
            if not scraper.login():
                click.echo("✗ Login failed!", err=True)
                return
            
            click.echo("✓ Login successful!")
            
            # Search candidates
            click.echo("Searching for candidates...")
            candidates = scraper.search_candidates(
                job_role=job_role,
                experience_min=exp_min,
                experience_max=exp_max,
                location=location,
                job_type=job_type,
                max_results=max_results
            )
            
            if not candidates:
                click.echo("No candidates found.")
                return
            
            click.echo(f"✓ Found {len(candidates)} candidates")
            
            # Save to database
            click.echo("Saving candidates to database...")
            dm.add_candidates_bulk(job_search.id, candidates)
            click.echo(f"✓ Saved {len(candidates)} candidates")
            
            # Export to Excel
            if click.confirm('Export to Excel?', default=True):
                filepath = dm.export_to_excel(job_search.id)
                click.echo(f"✓ Exported to: {filepath}")
        
        dm.close()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@cli.command()
@click.option('--job-search-id', type=int, required=True, help='Job search ID')
def list_candidates(job_search_id):
    """List all candidates for a job search."""
    try:
        dm = DataManager()
        candidates = dm.get_candidates_by_job_search(job_search_id)
        
        if not candidates:
            click.echo("No candidates found.")
            return
        
        click.echo(f"\nFound {len(candidates)} candidates:\n")
        
        for c in candidates:
            status = "✓ Contacted" if c.contacted else "○ Not contacted"
            interested = ""
            if c.interested is not None:
                interested = " | Interested: " + ("Yes" if c.interested else "No")
            
            click.echo(f"ID: {c.id} | {c.name} | {c.experience_years}y exp | {status}{interested}")
            if c.email:
                click.echo(f"    Email: {c.email}")
            if c.phone:
                click.echo(f"    Phone: {c.phone}")
            if c.current_company:
                click.echo(f"    Company: {c.current_company} ({c.current_designation})")
            click.echo()
        
        dm.close()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@cli.command()
@click.option('--job-search-id', type=int, help='Job search ID (optional)')
@click.option('--output', help='Output filename (optional)')
def export(job_search_id, output):
    """Export candidates to Excel."""
    try:
        dm = DataManager()
        filepath = dm.export_to_excel(job_search_id, output)
        
        if filepath:
            click.echo(f"✓ Exported to: {filepath}")
        else:
            click.echo("No candidates to export.")
        
        dm.close()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@cli.command()
@click.option('--job-search-id', type=int, required=True, help='Job search ID')
def stats(job_search_id):
    """Show statistics for a job search."""
    try:
        dm = DataManager()
        statistics = dm.get_statistics(job_search_id)
        
        click.echo("\n=== Statistics ===")
        click.echo(f"Total Candidates:      {statistics['total_candidates']}")
        click.echo(f"Contacted:             {statistics['contacted']}")
        click.echo(f"Pending Contact:       {statistics['pending_contact']}")
        click.echo(f"Interested:            {statistics['interested']}")
        click.echo(f"Not Interested:        {statistics['not_interested']}")
        click.echo(f"Interview Scheduled:   {statistics['interview_scheduled']}")
        click.echo()
        
        dm.close()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@cli.command()
@click.option('--candidate-id', type=int, required=True, help='Candidate ID')
@click.option('--contacted', type=bool, help='Mark as contacted')
@click.option('--interested', type=bool, help='Mark as interested')
@click.option('--comments', help='Add comments')
def update(candidate_id, contacted, interested, comments):
    """Update candidate status."""
    try:
        dm = DataManager()
        dm.update_candidate_status(
            candidate_id=candidate_id,
            contacted=contacted,
            interested=interested,
            comments=comments
        )
        click.echo(f"✓ Updated candidate {candidate_id}")
        dm.close()
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@cli.command()
@click.option('--job-search-id', type=int, required=True, help='Job search ID')
@click.option('--ai-tool', type=click.Choice(['n8n', 'make', 'custom']), default='n8n', help='AI tool to use')
@click.option('--custom-webhook', help='Custom webhook URL (for custom tool)')
@click.option('--job-role', required=True, help='Job role for script')
@click.option('--company-name', default='our company', help='Company name for script')
def trigger_calls(job_search_id, ai_tool, custom_webhook, job_role, company_name):
    """Trigger automated calls for candidates."""
    try:
        ai = AIIntegration()
        
        # Get candidates not yet contacted
        candidate_ids = ai.get_candidates_for_calling(job_search_id, contacted_only=False)
        
        if not candidate_ids:
            click.echo("No candidates found to call.")
            return
        
        click.echo(f"Found {len(candidate_ids)} candidates to call")
        
        if not click.confirm('Proceed with automated calls?'):
            return
        
        job_data = {
            'job_role': job_role,
            'company_name': company_name
        }
        
        click.echo(f"Triggering calls via {ai_tool}...")
        results = ai.trigger_automated_calls(
            candidate_ids=candidate_ids,
            job_data=job_data,
            ai_tool=ai_tool,
            custom_webhook=custom_webhook
        )
        
        success_count = sum(1 for r in results if r['status'] == 'sent')
        click.echo(f"✓ Triggered {success_count}/{len(results)} calls successfully")
        
        # Show failures
        failures = [r for r in results if r['status'] != 'sent']
        if failures:
            click.echo("\nFailed calls:")
            for f in failures:
                click.echo(f"  Candidate {f['candidate_id']}: {f.get('error', 'Unknown error')}")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


@cli.command()
@click.option('--host', default='0.0.0.0', help='API host')
@click.option('--port', default=5000, help='API port')
@click.option('--debug/--no-debug', default=False, help='Debug mode')
def serve(host, port, debug):
    """Start the REST API server."""
    try:
        from api import app
        click.echo(f"Starting API server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)


if __name__ == '__main__':
    cli()
