import { motion } from 'framer-motion';
import { FileText, Scale, AlertCircle, CheckCircle, XCircle, Shield } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="w-full py-16 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 border border-primary/30 rounded mb-6">
              <Scale className="w-4 h-4 text-primary" />
              <span className="text-sm font-paragraph text-primary">Last Updated: February 2026</span>
            </div>

            <h1 
              className="font-heading text-5xl lg:text-7xl font-black text-foreground mb-6"
            >
              Terms of <span className="text-primary">Service</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground font-semibold max-w-3xl mx-auto">
              Please read these terms carefully before using AI Nexus platform
            </p>
          </motion.div>

          <div className="max-w-4xl mx-auto space-y-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <FileText className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Acceptance of Terms</h2>
              </div>

              <div className="font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  By accessing and using AI Nexus ("the Platform"), you accept and agree to be bound by these Terms of Service. 
                  If you do not agree to these terms, please do not use the Platform. We reserve the right to modify these terms 
                  at any time, and your continued use constitutes acceptance of any changes.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Permitted Use</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">Educational Purpose:</strong> The Platform is designed for interview 
                  preparation and skill development. You may use it to practice interviews, receive feedback, and improve 
                  your communication skills.
                </p>
                <p>
                  <strong className="text-foreground">Personal Use:</strong> Your account is for your personal use only. 
                  You may not share your account credentials or allow others to use your account.
                </p>
                <p>
                  <strong className="text-foreground">Content Ownership:</strong> You retain ownership of your practice session 
                  recordings and data. We only use this data to provide services and improve our AI models as described in our 
                  Privacy Policy.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-destructive/10 rounded-lg flex items-center justify-center">
                  <XCircle className="w-6 h-6 text-destructive" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Prohibited Activities</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>You agree NOT to:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Use the Platform for any illegal or unauthorized purpose</li>
                  <li>Attempt to gain unauthorized access to our systems or other users' accounts</li>
                  <li>Upload malicious code, viruses, or any harmful content</li>
                  <li>Reverse engineer, decompile, or attempt to extract our AI models</li>
                  <li>Use automated tools (bots, scrapers) without explicit permission</li>
                  <li>Harass, abuse, or harm other users or our staff</li>
                  <li>Misrepresent your identity or affiliation</li>
                  <li>Violate any applicable laws or regulations</li>
                </ul>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">AI Feedback Disclaimer</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">Educational Tool:</strong> AI Nexus is an educational tool designed to help 
                  you improve your interview skills. It is NOT a substitute for professional career coaching or guaranteed 
                  interview success.
                </p>
                <p>
                  <strong className="text-foreground">AI Limitations:</strong> While our AI is highly advanced, it may not always 
                  be 100% accurate. Feedback should be used as guidance, not absolute truth.
                </p>
                <p>
                  <strong className="text-foreground">No Guarantees:</strong> We do not guarantee that using our Platform will 
                  result in job offers or interview success. Your success depends on many factors beyond our control.
                </p>
                <p>
                  <strong className="text-foreground">Bias Mitigation:</strong> We actively work to eliminate biases in our AI, 
                  but no system is perfect. If you believe you've received unfair feedback, please contact us.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Shield className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Intellectual Property</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">Platform Ownership:</strong> All content, features, and functionality of 
                  the Platform (including but not limited to software, text, graphics, logos, and AI models) are owned by 
                  AI Nexus and protected by copyright, trademark, and other intellectual property laws.
                </p>
                <p>
                  <strong className="text-foreground">Limited License:</strong> We grant you a limited, non-exclusive, 
                  non-transferable license to access and use the Platform for personal, educational purposes.
                </p>
                <p>
                  <strong className="text-foreground">Your Content:</strong> You retain ownership of your practice session 
                  recordings. By using the Platform, you grant us a license to process and analyze your content to provide 
                  services and improve our AI.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Scale className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Limitation of Liability</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  To the maximum extent permitted by law, AI Nexus shall not be liable for any indirect, incidental, special, 
                  consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, 
                  or any loss of data, use, goodwill, or other intangible losses resulting from:
                </p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Your use or inability to use the Platform</li>
                  <li>Any unauthorized access to or use of our servers and/or any personal information stored therein</li>
                  <li>Any interruption or cessation of transmission to or from the Platform</li>
                  <li>Any bugs, viruses, or the like that may be transmitted through the Platform by any third party</li>
                  <li>Any errors or omissions in any content or for any loss or damage incurred as a result of your use of any content</li>
                </ul>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8"
            >
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Account Termination</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">By You:</strong> You may terminate your account at any time through your 
                  profile settings. Upon termination, your data will be deleted according to our Privacy Policy.
                </p>
                <p>
                  <strong className="text-foreground">By Us:</strong> We reserve the right to suspend or terminate your account 
                  if you violate these Terms of Service, engage in prohibited activities, or for any other reason at our sole discretion.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.7 }}
              className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/30 rounded-lg p-8"
            >
              <h2 className="font-heading text-2xl font-bold text-foreground mb-6">Contact Us</h2>
              
              <div className="font-paragraph text-foreground/80 leading-relaxed">
                <p className="mb-4">
                  If you have questions about these Terms of Service, please contact us:
                </p>
                <p>
                  <strong className="text-foreground">Email:</strong>{' '}
                  <a href="mailto:legal@ainexus.com" className="text-primary hover:text-primary/80 transition-colors">
                    legal@ainexus.com
                  </a>
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
