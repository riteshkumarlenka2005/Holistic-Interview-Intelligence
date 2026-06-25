import { motion } from 'framer-motion';
import { Shield, Lock, Eye, Database, UserCheck, FileText } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function PrivacyPage() {
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
              <Shield className="w-4 h-4 text-primary" />
              <span className="text-sm font-paragraph text-primary">Last Updated: February 2026</span>
            </div>

            <h1 
              className="font-heading text-5xl lg:text-7xl font-black text-foreground mb-6"
            >
              Privacy <span className="text-primary">Policy</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground font-semibold max-w-3xl mx-auto">
              Your privacy is important to us. This policy explains how we collect, use, and protect your data.
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
                  <Database className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Information We Collect</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">Account Information:</strong> When you create an account, we collect your name, 
                  email address, and profile information.
                </p>
                <p>
                  <strong className="text-foreground">Practice Session Data:</strong> Video and audio recordings from your practice 
                  sessions, along with AI-generated analysis and feedback.
                </p>
                <p>
                  <strong className="text-foreground">Usage Data:</strong> Information about how you use our platform, including 
                  pages visited, features used, and time spent on the platform.
                </p>
                <p>
                  <strong className="text-foreground">Device Information:</strong> Browser type, operating system, IP address, 
                  and device identifiers for security and optimization purposes.
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
                  <Eye className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">How We Use Your Information</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">Provide Services:</strong> To deliver AI-powered interview analysis, 
                  feedback, and personalized recommendations.
                </p>
                <p>
                  <strong className="text-foreground">Improve Platform:</strong> To enhance our AI models, user experience, 
                  and develop new features based on usage patterns.
                </p>
                <p>
                  <strong className="text-foreground">Communication:</strong> To send you important updates, security alerts, 
                  and optional educational content (you can opt out anytime).
                </p>
                <p>
                  <strong className="text-foreground">Security:</strong> To protect against fraud, abuse, and unauthorized access 
                  to our platform.
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
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Lock className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Data Security</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">Encryption:</strong> All data is encrypted in transit using TLS and at rest 
                  using AES-256 encryption.
                </p>
                <p>
                  <strong className="text-foreground">Access Controls:</strong> Strict access controls ensure only authorized 
                  personnel can access user data, and only when necessary.
                </p>
                <p>
                  <strong className="text-foreground">Regular Audits:</strong> We conduct regular security audits and penetration 
                  testing to identify and fix vulnerabilities.
                </p>
                <p>
                  <strong className="text-foreground">Data Retention:</strong> Practice session recordings are retained for 90 days 
                  unless you choose to delete them earlier. Account data is retained until you delete your account.
                </p>
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
                  <UserCheck className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Your Rights</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">Access:</strong> You can access and download all your personal data at any time 
                  through your profile settings.
                </p>
                <p>
                  <strong className="text-foreground">Correction:</strong> You can update or correct your personal information 
                  through your account settings.
                </p>
                <p>
                  <strong className="text-foreground">Deletion:</strong> You can delete your account and all associated data at any time. 
                  This action is permanent and cannot be undone.
                </p>
                <p>
                  <strong className="text-foreground">Opt-Out:</strong> You can opt out of non-essential communications and data 
                  collection features at any time.
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
                  <FileText className="w-6 h-6 text-primary" />
                </div>
                <h2 className="font-heading text-2xl font-bold text-foreground">Third-Party Sharing</h2>
              </div>

              <div className="space-y-4 font-paragraph text-foreground/80 leading-relaxed">
                <p>
                  <strong className="text-foreground">We Do NOT:</strong> Sell, rent, or share your personal data with third parties 
                  for marketing purposes.
                </p>
                <p>
                  <strong className="text-foreground">Service Providers:</strong> We work with trusted service providers (cloud hosting, 
                  analytics) who are bound by strict confidentiality agreements.
                </p>
                <p>
                  <strong className="text-foreground">Legal Requirements:</strong> We may disclose information if required by law, 
                  court order, or to protect our rights and safety.
                </p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="bg-gradient-to-br from-primary/5 to-secondary/5 border border-primary/30 rounded-lg p-8"
            >
              <h2 className="font-heading text-2xl font-bold text-foreground mb-6">Contact Us</h2>
              
              <div className="font-paragraph text-foreground/80 leading-relaxed">
                <p className="mb-4">
                  If you have questions about this Privacy Policy or how we handle your data, please contact us:
                </p>
                <p>
                  <strong className="text-foreground">Email:</strong>{' '}
                  <a href="mailto:privacy@ainexus.com" className="text-primary hover:text-primary/80 transition-colors">
                    privacy@ainexus.com
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
