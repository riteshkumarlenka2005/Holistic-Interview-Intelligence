import { motion } from 'framer-motion';
import { User, Mail, Calendar, Award, TrendingUp, Video } from 'lucide-react';
import { useMember } from '@/integrations';
import { Button } from '@/components/ui/button';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';

export default function ProfilePage() {
  const { member, actions } = useMember();

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />

      <div className="w-full py-16 px-8 lg:px-16">
        <div className="max-w-[100rem] mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <h1
              className="font-heading text-5xl lg:text-6xl font-black text-foreground mb-4"
            >
              Your <span className="text-primary">Profile</span>
            </h1>
            <p className="font-paragraph text-lg text-foreground font-semibold">
              Manage your account and view your information
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Profile Info */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="lg:col-span-2"
            >
              <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-8">
                <h2 className="font-heading text-2xl font-bold text-foreground mb-8">Account Information</h2>

                <div className="space-y-6">
                  <div className="flex items-start gap-4 p-4 bg-background/50 border border-primary/20 rounded">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="font-paragraph text-sm text-foreground/60 mb-1">Display Name</div>
                      <div className="font-heading text-lg font-semibold text-foreground">
                        {member?.profile?.nickname || 'Not set'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start gap-4 p-4 bg-background/50 border border-primary/20 rounded">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="font-paragraph text-sm text-foreground/60 mb-1">Full Name</div>
                      <div className="font-heading text-lg font-semibold text-foreground">
                        {member?.firstName && member?.lastName
                          ? `${member.firstName} ${member.lastName}`
                          : 'Not set'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-start gap-4 p-4 bg-background/50 border border-primary/20 rounded">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Mail className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="font-paragraph text-sm text-foreground/60 mb-1">Email Address</div>
                      <div className="font-heading text-lg font-semibold text-foreground">
                        {member?.email || 'Not available'}
                      </div>
                      {member?.isVerified && (
                        <div className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-primary/10 border border-primary/30 rounded text-xs font-paragraph text-primary">
                          <Award className="w-3 h-3" />
                          Verified
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-start gap-4 p-4 bg-background/50 border border-primary/20 rounded">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Calendar className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="font-paragraph text-sm text-foreground/60 mb-1">Member Since</div>
                      <div className="font-heading text-lg font-semibold text-foreground">
                        {member?.createdAt
                          ? format(new Date(member.createdAt), 'MMMM dd, yyyy')
                          : 'Unknown'}
                      </div>
                    </div>
                  </div>

                  {member?.updatedAt && (
                    <div className="flex items-start gap-4 p-4 bg-background/50 border border-primary/20 rounded">
                      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Calendar className="w-6 h-6 text-primary" />
                      </div>
                      <div className="flex-1">
                        <div className="font-paragraph text-sm text-foreground/60 mb-1">Last Login</div>
                        <div className="font-heading text-lg font-semibold text-foreground">
                          {format(new Date(member.updatedAt), 'MMMM dd, yyyy • h:mm a')}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="space-y-6"
            >
              <div className="bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-6">
                <h3 className="font-heading text-xl font-bold text-foreground mb-6">Quick Actions</h3>

                <div className="space-y-3">
                  <Link to="/dashboard">
                    <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90 rounded justify-start">
                      <TrendingUp className="w-5 h-5 mr-2" />
                      View Dashboard
                    </Button>
                  </Link>

                  <Link to="/practice">
                    <Button variant="outline" className="w-full border-primary/30 text-primary hover:bg-primary/10 rounded justify-start">
                      <Video className="w-5 h-5 mr-2" />
                      Practice Sessions
                    </Button>
                  </Link>

                  <Link to="/progress">
                    <Button variant="outline" className="w-full border-primary/30 text-primary hover:bg-primary/10 rounded justify-start">
                      <Award className="w-5 h-5 mr-2" />
                      View Progress
                    </Button>
                  </Link>
                </div>
              </div>

              <div className="bg-gradient-to-br from-secondary/10 to-secondary/5 border border-secondary/30 rounded-lg p-6">
                <h3 className="font-heading text-xl font-bold text-foreground mb-4">Account Status</h3>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-paragraph text-sm text-foreground/70">Status</span>
                    <span className="font-paragraph text-sm font-semibold text-secondary capitalize">
                      {member?.isVerified ? 'Active' : 'Pending'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="font-paragraph text-sm text-foreground/70">Plan</span>
                    <span className="font-paragraph text-sm font-semibold text-secondary">Free</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-background to-gradient-start/10 border border-primary/30 rounded-lg p-6">
                <h3 className="font-heading text-lg font-bold text-foreground mb-4">Account Actions</h3>

                <Button
                  onClick={actions.logout}
                  variant="outline"
                  className="w-full border-destructive/30 text-destructive hover:bg-destructive/10 rounded"
                >
                  Sign Out
                </Button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
