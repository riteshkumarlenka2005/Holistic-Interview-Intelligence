import { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, MessageSquare, Send, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { BaseCrudService } from '@/integrations';
import { ContactInquiries } from '@/entities';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    userName: '',
    emailAddress: '',
    subject: '',
    messageContent: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const newInquiry: ContactInquiries = {
      _id: crypto.randomUUID(),
      userName: formData.userName,
      emailAddress: formData.emailAddress,
      subject: formData.subject,
      messageContent: formData.messageContent,
      submissionDate: new Date().toISOString(),
      status: 'pending'
    };

    setIsSubmitting(true);
    
    try {
      await BaseCrudService.create('contactinquiries', newInquiry);
      setIsSubmitted(true);
      setFormData({ userName: '', emailAddress: '', subject: '', messageContent: '' });
    } catch (error) {
      console.error('Failed to submit inquiry:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

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
            <h1 
              className="font-heading text-6xl lg:text-8xl font-black text-foreground mb-6"
            >
              Get in <span className="text-primary">Touch</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground font-semibold max-w-3xl mx-auto">
              Have questions or feedback? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-2 gap-12 items-start">
            {/* Contact Form */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              {isSubmitted ? (
                <div className="bg-gradient-to-br from-primary/10 to-secondary/10 border border-primary/30 rounded-lg p-12 text-center">
                  <div className="w-20 h-20 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <CheckCircle className="w-10 h-10 text-primary" />
                  </div>
                  <h2 className="font-heading text-3xl font-bold text-foreground mb-4">Message Sent!</h2>
                  <p className="font-paragraph text-foreground/70 mb-8">
                    Thank you for reaching out. We'll get back to you within 24-48 hours.
                  </p>
                  <Button
                    onClick={() => setIsSubmitted(false)}
                    variant="outline"
                    className="border-primary/30 text-primary hover:bg-primary/10 rounded"
                  >
                    Send Another Message
                  </Button>
                </div>
              ) : (
                <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                      <label htmlFor="userName" className="block font-paragraph text-sm font-semibold text-foreground mb-2">
                        Your Name
                      </label>
                      <Input
                        id="userName"
                        name="userName"
                        type="text"
                        required
                        value={formData.userName}
                        onChange={handleChange}
                        placeholder="John Doe"
                        className="bg-background border-primary/30 text-foreground placeholder:text-foreground/50 rounded h-12 font-paragraph"
                      />
                    </div>

                    <div>
                      <label htmlFor="emailAddress" className="block font-paragraph text-sm font-semibold text-foreground mb-2">
                        Email Address
                      </label>
                      <Input
                        id="emailAddress"
                        name="emailAddress"
                        type="email"
                        required
                        value={formData.emailAddress}
                        onChange={handleChange}
                        placeholder="john@example.com"
                        className="bg-background border-primary/30 text-foreground placeholder:text-foreground/50 rounded h-12 font-paragraph"
                      />
                    </div>

                    <div>
                      <label htmlFor="subject" className="block font-paragraph text-sm font-semibold text-foreground mb-2">
                        Subject
                      </label>
                      <Input
                        id="subject"
                        name="subject"
                        type="text"
                        required
                        value={formData.subject}
                        onChange={handleChange}
                        placeholder="How can we help?"
                        className="bg-background border-primary/30 text-foreground placeholder:text-foreground/50 rounded h-12 font-paragraph"
                      />
                    </div>

                    <div>
                      <label htmlFor="messageContent" className="block font-paragraph text-sm font-semibold text-foreground mb-2">
                        Message
                      </label>
                      <Textarea
                        id="messageContent"
                        name="messageContent"
                        required
                        value={formData.messageContent}
                        onChange={handleChange}
                        placeholder="Tell us more about your inquiry..."
                        rows={6}
                        className="bg-background border-primary/30 text-foreground placeholder:text-foreground/50 rounded font-paragraph resize-none"
                      />
                    </div>

                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded py-6 text-lg font-semibold"
                    >
                      {isSubmitting ? (
                        'Sending...'
                      ) : (
                        <>
                          <Send className="w-5 h-5 mr-2" />
                          Send Message
                        </>
                      )}
                    </Button>
                  </form>
                </div>
              )}
            </motion.div>

            {/* Contact Info */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="space-y-8"
            >
              <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
                    <Mail className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="font-heading text-2xl font-bold text-foreground">Email Us</h3>
                </div>
                <p className="font-paragraph text-foreground/70 mb-4">
                  For general inquiries and support
                </p>
                <a href="mailto:support@ainexus.com" className="font-paragraph text-primary hover:text-primary/80 transition-colors">
                  support@ainexus.com
                </a>
              </div>

              <div className="bg-gradient-to-br from-secondary/10 to-secondary/5 border border-secondary/30 rounded-lg p-8">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 bg-secondary/20 rounded-lg flex items-center justify-center">
                    <MessageSquare className="w-6 h-6 text-secondary" />
                  </div>
                  <h3 className="font-heading text-2xl font-bold text-foreground">Response Time</h3>
                </div>
                <p className="font-paragraph text-foreground/70">
                  We typically respond to all inquiries within 24-48 hours during business days. 
                  For urgent matters, please mark your subject line with "URGENT".
                </p>
              </div>

              <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8">
                <h3 className="font-heading text-xl font-bold text-foreground mb-4">Office Hours</h3>
                <div className="space-y-2 font-paragraph text-sm text-foreground/70">
                  <div className="flex justify-between">
                    <span>Monday - Friday</span>
                    <span className="text-foreground">9:00 AM - 6:00 PM EST</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Saturday</span>
                    <span className="text-foreground">10:00 AM - 4:00 PM EST</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Sunday</span>
                    <span className="text-foreground">Closed</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
