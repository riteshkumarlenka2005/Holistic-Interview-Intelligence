import { Link } from 'react-router-dom';
import { Brain, Mail, Globe, Linkedin, Twitter, Github, Heart } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full bg-card-bg border-t border-border-color">
      <div className="max-w-[100rem] mx-auto px-6 py-16 lg:px-12">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div className="space-y-6">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center group-hover:shadow-lg transition-shadow duration-300">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading text-xl font-bold text-foreground hidden sm:inline">
                Interview<span className="text-primary">Pro</span>
              </span>
            </Link>
            <p className="font-paragraph text-sm text-foreground-muted">
              Empowering students and professionals with AI-driven interview preparation. 
              Committed to accessible, quality education for all.
            </p>
            <div className="flex items-center gap-3">
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 bg-secondary rounded-lg flex items-center justify-center hover:bg-accent-light transition-colors duration-300"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-4 h-4 text-primary" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 bg-secondary rounded-lg flex items-center justify-center hover:bg-accent-light transition-colors duration-300"
                aria-label="Twitter"
              >
                <Twitter className="w-4 h-4 text-primary" />
              </a>
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 bg-secondary rounded-lg flex items-center justify-center hover:bg-accent-light transition-colors duration-300"
                aria-label="GitHub"
              >
                <Github className="w-4 h-4 text-primary" />
              </a>
            </div>
          </div>

          {/* Platform */}
          <div>
            <h3 className="font-heading text-base font-bold text-foreground mb-6">Platform</h3>
            <ul className="space-y-3">
              <li>
                <Link to="/features" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Features
                </Link>
              </li>
              <li>
                <Link to="/practice" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Practice Interview
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/progress" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Progress Tracking
                </Link>
              </li>
              <li>
                <Link to="/resources" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Learning Resources
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-heading text-base font-bold text-foreground mb-6">Company</h3>
            <ul className="space-y-3">
              <li>
                <Link to="/about" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/about#mission" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Our Mission
                </Link>
              </li>
              <li>
                <Link to="/about#values" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Values & Ethics
                </Link>
              </li>
              <li>
                <Link to="/contact" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Contact */}
          <div>
            <h3 className="font-heading text-base font-bold text-foreground mb-6">Legal & Support</h3>
            <ul className="space-y-3">
              <li>
                <Link to="/privacy" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300">
                  Terms of Service
                </Link>
              </li>
              <li>
                <a href="mailto:support@interviewpro.com" className="font-paragraph text-sm text-foreground-muted hover:text-primary transition-colors duration-300 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  support@interviewpro.com
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Mission Banner */}
        <div className="bg-secondary border border-border-color rounded-xl p-6 mb-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Globe className="w-8 h-8 text-primary flex-shrink-0" />
              <div>
                <h4 className="font-heading text-base font-bold text-foreground mb-1">
                  Democratizing Interview Preparation
                </h4>
                <p className="font-paragraph text-sm text-foreground-muted">
                  Making quality career preparation accessible to students and professionals worldwide
                </p>
              </div>
            </div>
            <Link to="/about">
              <span className="font-paragraph text-sm text-primary hover:text-accent-purple transition-colors duration-300 whitespace-nowrap">
                Learn More →
              </span>
            </Link>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-border-color">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="font-paragraph text-sm text-foreground-muted">
              © {currentYear} InterviewPro. All rights reserved.
            </p>
            <p className="font-paragraph text-sm text-foreground-muted flex items-center gap-2">
              Built with <Heart className="w-4 h-4 text-primary fill-primary" /> for accessible education
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
