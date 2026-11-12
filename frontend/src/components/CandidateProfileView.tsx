import React, { useState } from 'react';
import {
  User, Briefcase, Code, GraduationCap, FolderGit2, Award,
  Save, Download, FileSpreadsheet, Plus, Trash2, Check,
  ExternalLink, Mail, Phone, MapPin, Linkedin, Github, Globe
} from 'lucide-react';
import { CandidateProfile, CategorizedSkills, EmploymentHistoryItem, EducationItem } from '../types/candidate';
import { ConfidenceBadge } from './ConfidenceBadge';
import { MissingFieldAlert } from './MissingFieldAlert';
import { api } from '../services/api';

interface Props {
  candidate: CandidateProfile;
  onUpdateSuccess: (updated: CandidateProfile) => void;
}

export const CandidateProfileView: React.FC<Props> = ({ candidate, onUpdateSuccess }) => {
  const [profile, setProfile] = useState<CandidateProfile>(candidate);
  const [activeTab, setActiveTab] = useState<'overview' | 'experience' | 'skills' | 'education' | 'projects'>('overview');
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState(false);
  const [newSkillText, setNewSkillText] = useState('');
  const [selectedSkillCategory, setSelectedSkillCategory] = useState<keyof CategorizedSkills>('programming_languages');

  // Personal Info change handler
  const handlePersonalChange = (field: string, value: string) => {
    setProfile((prev) => ({
      ...prev,
      personal_information: {
        ...prev.personal_information,
        [field]: value,
      },
    }));
  };

  // Professional summary change handler
  const handleSummaryChange = (value: string) => {
    setProfile((prev) => ({
      ...prev,
      professional_information: {
        ...prev.professional_information,
        summary: value,
      },
    }));
  };

  // Job History update
  const handleJobChange = (index: number, field: keyof EmploymentHistoryItem, value: any) => {
    setProfile((prev) => {
      const updatedHistory = [...prev.professional_information.employment_history];
      updatedHistory[index] = {
        ...updatedHistory[index],
        [field]: value,
      };
      return {
        ...prev,
        professional_information: {
          ...prev.professional_information,
          employment_history: updatedHistory,
        },
      };
    });
  };

  const handleAddJob = () => {
    const newJob: EmploymentHistoryItem = {
      company_name: 'New Company',
      job_title: 'Software Engineer',
      start_date: '2022-01',
      end_date: 'Present',
      is_current: true,
      duration_months: 12,
      responsibilities: 'Key responsibilities and achievements...',
      confidence_score: 1.0,
    };
    setProfile((prev) => ({
      ...prev,
      professional_information: {
        ...prev.professional_information,
        employment_history: [newJob, ...prev.professional_information.employment_history],
      },
    }));
  };

  const handleDeleteJob = (index: number) => {
    setProfile((prev) => {
      const updatedHistory = prev.professional_information.employment_history.filter((_, i) => i !== index);
      return {
        ...prev,
        professional_information: {
          ...prev.professional_information,
          employment_history: updatedHistory,
        },
      };
    });
  };

  // Skills handlers
  const handleRemoveSkill = (category: keyof CategorizedSkills, skillName: string) => {
    setProfile((prev) => ({
      ...prev,
      skills: {
        ...prev.skills,
        [category]: prev.skills[category].filter((s) => s !== skillName),
      },
    }));
  };

  const handleAddSkill = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkillText.trim()) return;
    const trimmed = newSkillText.trim();
    setProfile((prev) => {
      const existing = prev.skills[selectedSkillCategory] || [];
      if (existing.includes(trimmed)) return prev;
      return {
        ...prev,
        skills: {
          ...prev.skills,
          [selectedSkillCategory]: [...existing, trimmed],
        },
      };
    });
    setNewSkillText('');
  };

  // Education handlers
  const handleEduChange = (index: number, field: keyof EducationItem, value: any) => {
    setProfile((prev) => {
      const updatedEdu = [...prev.education];
      updatedEdu[index] = {
        ...updatedEdu[index],
        [field]: value,
      };
      return {
        ...prev,
        education: updatedEdu,
      };
    });
  };

  const handleAddEdu = () => {
    const newEdu: EducationItem = {
      degree: 'Degree / Major',
      institution: 'University / College',
      university: 'University',
      specialization: 'Field of Study',
      graduation_year: '2023',
      score: null,
      confidence_score: 1.0,
    };
    setProfile((prev) => ({
      ...prev,
      education: [...prev.education, newEdu],
    }));
  };

  const handleDeleteEdu = (index: number) => {
    setProfile((prev) => ({
      ...prev,
      education: prev.education.filter((_, i) => i !== index),
    }));
  };

  // Save to backend
  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccessMsg(false);
    try {
      const updated = await api.updateCandidate(profile.id, profile);
      setProfile(updated);
      onUpdateSuccess(updated);
      setSaveSuccessMsg(true);
      setTimeout(() => setSaveSuccessMsg(false), 3000);
    } catch (err) {
      console.error('Save error:', err);
      alert('Failed to save candidate updates.');
    } finally {
      setIsSaving(false);
    }
  };

  const candidateName = profile.personal_information.full_name || 'Candidate';

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header Profile Bar */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                {profile.personal_information.full_name || (
                  <span className="text-slate-400 italic">Name Not Found (null)</span>
                )}
              </h1>
              <ConfidenceBadge score={profile.overall_confidence} label="Overall Score" />
            </div>
            <p className="text-sm text-slate-600 mt-1 flex items-center gap-2">
              <span className="font-semibold text-slate-800">
                {profile.professional_information.current_job_title || 'Professional'}
              </span>
              {profile.professional_information.current_company && (
                <>
                  <span className="text-slate-400">•</span>
                  <span>{profile.professional_information.current_company}</span>
                </>
              )}
              <span className="text-slate-400">•</span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-brand-700 border border-blue-200">
                {profile.professional_information.total_experience_years} yrs Total Experience (Overlap-Free)
              </span>
            </p>
          </div>

          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold hover:bg-emerald-700 transition shadow-sm disabled:opacity-50"
            >
              {saveSuccessMsg ? <Check className="w-4 h-4 text-white" /> : <Save className="w-4 h-4" />}
              <span>{saveSuccessMsg ? 'Saved!' : isSaving ? 'Saving...' : 'Save Profile'}</span>
            </button>

            <button
              onClick={() => api.downloadJson(profile.id, candidateName)}
              className="flex items-center gap-2 px-3.5 py-2 bg-white text-slate-700 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 transition shadow-sm"
              title="Download parsed candidate profile as JSON"
            >
              <Download className="w-4 h-4 text-slate-500" />
              <span>Export JSON</span>
            </button>

            <button
              onClick={() => api.downloadExcel(profile.id, candidateName)}
              className="flex items-center gap-2 px-3.5 py-2 bg-white text-slate-700 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 transition shadow-sm"
              title="Download formatted multi-tab Excel workbook"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-600" />
              <span>Export Excel</span>
            </button>
          </div>
        </div>
      </div>

      {/* Missing Fields Banner */}
      <MissingFieldAlert missingFields={profile.missing_fields} />

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 mb-6 space-x-1 sm:space-x-4 overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-sm border-b-2 transition whitespace-nowrap ${activeTab === 'overview'
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
        >
          <User className="w-4 h-4" /> Personal & Overview
        </button>

        <button
          onClick={() => setActiveTab('experience')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-sm border-b-2 transition whitespace-nowrap ${activeTab === 'experience'
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
        >
          <Briefcase className="w-4 h-4" /> Work Experience ({profile.professional_information.employment_history.length})
        </button>

        <button
          onClick={() => setActiveTab('skills')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-sm border-b-2 transition whitespace-nowrap ${activeTab === 'skills'
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
        >
          <Code className="w-4 h-4" /> Technical Skills
        </button>

        <button
          onClick={() => setActiveTab('education')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-sm border-b-2 transition whitespace-nowrap ${activeTab === 'education'
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
        >
          <GraduationCap className="w-4 h-4" /> Education ({profile.education.length})
        </button>

        <button
          onClick={() => setActiveTab('projects')}
          className={`flex items-center gap-2 py-3 px-4 font-semibold text-sm border-b-2 transition whitespace-nowrap ${activeTab === 'projects'
              ? 'border-brand-700 text-brand-700'
              : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
        >
          <FolderGit2 className="w-4 h-4" /> Projects & Credentials ({profile.projects.length + profile.certifications.length})
        </button>
      </div>

      {/* TAB 1: PERSONAL & OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {/* Executive Summary */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center justify-between">
                <span>Professional Summary</span>
                {profile.professional_information.summary ? (
                  <span className="text-xs text-emerald-600 font-medium">Extracted</span>
                ) : (
                  <span className="text-xs text-slate-400">Not provided</span>
                )}
              </h3>
              <textarea
                rows={4}
                value={profile.professional_information.summary || ''}
                onChange={(e) => handleSummaryChange(e.target.value)}
                placeholder="Enter candidate professional summary or objective..."
                className="w-full text-sm p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:outline-none text-slate-800"
              />
            </div>

            {/* Contact & Social Form */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-4">Contact & Identity Details</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                    <span>Full Legal Name</span>
                    <ConfidenceBadge score={profile.personal_information.confidence?.full_name} showIcon={false} />
                  </label>
                  <input
                    type="text"
                    value={profile.personal_information.full_name || ''}
                    onChange={(e) => handlePersonalChange('full_name', e.target.value)}
                    placeholder="Candidate Name"
                    className="w-full text-sm p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                    <span>Email Address</span>
                    <ConfidenceBadge score={profile.personal_information.confidence?.email} showIcon={false} />
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="email"
                      value={profile.personal_information.email || ''}
                      onChange={(e) => handlePersonalChange('email', e.target.value)}
                      placeholder="email@example.com"
                      className="w-full text-sm pl-9 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                    <span>Phone Number</span>
                    <ConfidenceBadge score={profile.personal_information.confidence?.phone} showIcon={false} />
                  </label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      value={profile.personal_information.phone || ''}
                      onChange={(e) => handlePersonalChange('phone', e.target.value)}
                      placeholder="+1-555-0100"
                      className="w-full text-sm pl-9 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                    <span>Location (City, State, Country)</span>
                    <ConfidenceBadge score={profile.personal_information.confidence?.location} showIcon={false} />
                  </label>
                  <div className="relative">
                    <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      value={profile.personal_information.location || ''}
                      onChange={(e) => handlePersonalChange('location', e.target.value)}
                      placeholder="City, State"
                      className="w-full text-sm pl-9 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                    <span>LinkedIn Profile</span>
                    <ConfidenceBadge score={profile.personal_information.confidence?.linkedin} showIcon={false} />
                  </label>
                  <div className="relative">
                    <Linkedin className="w-4 h-4 text-blue-600 absolute left-3 top-3" />
                    <input
                      type="text"
                      value={profile.personal_information.linkedin || ''}
                      onChange={(e) => handlePersonalChange('linkedin', e.target.value)}
                      placeholder="https://linkedin.com/in/..."
                      className="w-full text-sm pl-9 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                    <span>GitHub Profile</span>
                    <ConfidenceBadge score={profile.personal_information.confidence?.github} showIcon={false} />
                  </label>
                  <div className="relative">
                    <Github className="w-4 h-4 text-slate-800 absolute left-3 top-3" />
                    <input
                      type="text"
                      value={profile.personal_information.github || ''}
                      onChange={(e) => handlePersonalChange('github', e.target.value)}
                      placeholder="https://github.com/..."
                      className="w-full text-sm pl-9 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-600 mb-1 flex items-center justify-between">
                    <span>Portfolio Website</span>
                    <ConfidenceBadge score={profile.personal_information.confidence?.portfolio} showIcon={false} />
                  </label>
                  <div className="relative">
                    <Globe className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      value={profile.personal_information.portfolio || ''}
                      onChange={(e) => handlePersonalChange('portfolio', e.target.value)}
                      placeholder="https://portfolio.dev"
                      className="w-full text-sm pl-9 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Metrics Column */}
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-4">Experience Audit</h3>
              <div className="space-y-4">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500">Calculated Career Tenure</span>
                  <div className="text-2xl font-extrabold text-brand-900 mt-1">
                    {profile.professional_information.total_experience_years} Years
                  </div>
                  <span className="text-[11px] text-emerald-600 font-medium">
                    ✓ Overlap-free unique calendar duration
                  </span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500">Current / Most Recent Role</span>
                  <div className="text-sm font-bold text-slate-800 mt-1">
                    {profile.professional_information.current_job_title || 'N/A'}
                  </div>
                  <div className="text-xs text-slate-600">
                    {profile.professional_information.current_company || 'N/A'}
                  </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500">Known Languages</span>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {profile.languages.length > 0 ? (
                      profile.languages.map((l) => (
                        <span key={l} className="px-2 py-0.5 bg-white border border-slate-200 rounded-md text-xs font-medium text-slate-700">
                          {l}
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400">Not specified</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: WORK EXPERIENCE */}
      {activeTab === 'experience' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">Employment Timeline & Records</h3>
            <button
              onClick={handleAddJob}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200 rounded-lg hover:bg-brand-100 transition"
            >
              <Plus className="w-3.5 h-3.5" /> Add Job Record
            </button>
          </div>

          <div className="space-y-4">
            {profile.professional_information.employment_history.map((job, idx) => (
              <div key={idx} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative">
                <button
                  onClick={() => handleDeleteJob(idx)}
                  className="absolute top-6 right-6 text-slate-400 hover:text-rose-600 transition"
                  title="Remove this position"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4 pr-8">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Company / Organization</label>
                    <input
                      type="text"
                      value={job.company_name}
                      onChange={(e) => handleJobChange(idx, 'company_name', e.target.value)}
                      className="w-full text-sm font-semibold p-2 border border-slate-200 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Job Title / Role</label>
                    <input
                      type="text"
                      value={job.job_title}
                      onChange={(e) => handleJobChange(idx, 'job_title', e.target.value)}
                      className="w-full text-sm font-semibold p-2 border border-slate-200 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Tenure Duration</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={job.start_date || ''}
                        onChange={(e) => handleJobChange(idx, 'start_date', e.target.value)}
                        placeholder="YYYY-MM"
                        className="w-1/2 text-xs p-2 border border-slate-200 rounded-lg text-center"
                      />
                      <span className="text-slate-400">to</span>
                      <input
                        type="text"
                        value={job.end_date || ''}
                        onChange={(e) => handleJobChange(idx, 'end_date', e.target.value)}
                        placeholder="Present"
                        className="w-1/2 text-xs p-2 border border-slate-200 rounded-lg text-center"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 mb-3">
                  <label className="flex items-center gap-2 text-xs font-medium text-slate-600 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={job.is_current}
                      onChange={(e) => handleJobChange(idx, 'is_current', e.target.checked)}
                      className="rounded text-brand-600 focus:ring-brand-500"
                    />
                    <span>Active Current Position</span>
                  </label>
                  <span className="text-slate-300">|</span>
                  <span className="text-xs text-slate-500">
                    Duration: {job.duration_months} months
                  </span>
                  <ConfidenceBadge score={job.confidence_score} showIcon={false} />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Key Responsibilities & Impact</label>
                  <textarea
                    rows={3}
                    value={job.responsibilities || ''}
                    onChange={(e) => handleJobChange(idx, 'responsibilities', e.target.value)}
                    className="w-full text-sm p-2.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: TECHNICAL SKILLS */}
      {activeTab === 'skills' && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Categorized Technical Skills</h3>
              <p className="text-xs text-slate-500">
                Skills extracted verbatim from resume and categorized into taxonomy groups.
              </p>
            </div>

            {/* Add skill input */}
            <form onSubmit={handleAddSkill} className="flex items-center gap-2">
              <select
                value={selectedSkillCategory}
                onChange={(e) => setSelectedSkillCategory(e.target.value as keyof CategorizedSkills)}
                className="text-xs p-2 border border-slate-200 rounded-lg bg-slate-50 font-medium"
              >
                <option value="programming_languages">Languages</option>
                <option value="frameworks">Frameworks</option>
                <option value="libraries">Libraries</option>
                <option value="databases">Databases</option>
                <option value="cloud">Cloud & DevOps</option>
                <option value="ai_ml">AI / ML</option>
                <option value="tools">Tools</option>
                <option value="other_skills">Other</option>
              </select>
              <input
                type="text"
                value={newSkillText}
                onChange={(e) => setNewSkillText(e.target.value)}
                placeholder="Add skill..."
                className="text-xs p-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-brand-500"
              />
              <button
                type="submit"
                className="px-3 py-2 bg-brand-900 text-white text-xs font-semibold rounded-lg hover:bg-brand-800"
              >
                Add
              </button>
            </form>
          </div>

          {/* Categorized groups */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {(
              [
                ['programming_languages', 'Programming Languages', 'bg-blue-50 text-blue-800 border-blue-200'],
                ['frameworks', 'Frameworks', 'bg-indigo-50 text-indigo-800 border-indigo-200'],
                ['libraries', 'Libraries', 'bg-cyan-50 text-cyan-800 border-cyan-200'],
                ['databases', 'Databases', 'bg-emerald-50 text-emerald-800 border-emerald-200'],
                ['cloud', 'Cloud & Infrastructure', 'bg-sky-50 text-sky-800 border-sky-200'],
                ['ai_ml', 'AI & Machine Learning', 'bg-purple-50 text-purple-800 border-purple-200'],
                ['tools', 'Development Tools', 'bg-slate-100 text-slate-800 border-slate-200'],
                ['other_skills', 'Other Skills', 'bg-amber-50 text-amber-800 border-amber-200'],
              ] as const
            ).map(([catKey, title, badgeColor]) => {
              const list = profile.skills[catKey] || [];
              return (
                <div key={catKey} className="p-4 rounded-xl border border-slate-100 bg-slate-50/50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                      {title} ({list.length})
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {list.length > 0 ? (
                      list.map((s) => (
                        <span
                          key={s}
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium border ${badgeColor}`}
                        >
                          {s}
                          <button
                            type="button"
                            onClick={() => handleRemoveSkill(catKey, s)}
                            className="hover:opacity-75 transition"
                            title="Remove skill"
                          >
                            ×
                          </button>
                        </span>
                      ))
                    ) : (
                      <span className="text-xs text-slate-400 italic">No skills identified in this category</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 4: EDUCATION */}
      {activeTab === 'education' && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900">Academic Background & Education</h3>
            <button
              onClick={handleAddEdu}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200 rounded-lg hover:bg-brand-100 transition"
            >
              <Plus className="w-3.5 h-3.5" /> Add Education
            </button>
          </div>

          <div className="space-y-4">
            {profile.education.map((edu, idx) => (
              <div key={idx} className="p-5 rounded-xl border border-slate-200 bg-slate-50/30 relative">
                <button
                  onClick={() => handleDeleteEdu(idx)}
                  className="absolute top-5 right-5 text-slate-400 hover:text-rose-600 transition"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pr-8">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Degree / Qualification</label>
                    <input
                      type="text"
                      value={edu.degree || ''}
                      onChange={(e) => handleEduChange(idx, 'degree', e.target.value)}
                      placeholder="e.g. Bachelor of Science"
                      className="w-full text-sm font-semibold p-2 border border-slate-200 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">College / University</label>
                    <input
                      type="text"
                      value={edu.institution || ''}
                      onChange={(e) => handleEduChange(idx, 'institution', e.target.value)}
                      placeholder="Institution Name"
                      className="w-full text-sm font-semibold p-2 border border-slate-200 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Graduation Year</label>
                    <input
                      type="text"
                      value={edu.graduation_year || ''}
                      onChange={(e) => handleEduChange(idx, 'graduation_year', e.target.value)}
                      placeholder="YYYY"
                      className="w-full text-sm p-2 border border-slate-200 rounded-lg text-center"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: PROJECTS & CREDENTIALS */}
      {activeTab === 'projects' && (
        <div className="space-y-6">
          {/* Projects */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-4">Key Projects</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {profile.projects.map((proj, idx) => (
                <div key={idx} className="p-4 rounded-xl border border-slate-200 bg-slate-50/40">
                  <div className="flex items-start justify-between">
                    <h4 className="font-bold text-slate-900 text-sm">{proj.title}</h4>
                    {proj.link && (
                      <a href={proj.link} target="_blank" rel="noreferrer" className="text-brand-600 hover:text-brand-800">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                  {proj.technologies && (
                    <div className="text-xs text-brand-700 font-medium mt-1">Tech: {proj.technologies}</div>
                  )}
                  <p className="text-xs text-slate-600 mt-2">{proj.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-4">Certifications & Accreditations</h3>
            <div className="space-y-2">
              {profile.certifications.map((cert, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-slate-100 bg-slate-50">
                  <div className="flex items-center gap-2">
                    <Award className="w-4 h-4 text-brand-600" />
                    <span className="text-sm font-semibold text-slate-800">{cert.name}</span>
                  </div>
                  <span className="text-xs text-slate-500">{cert.issue_date || 'Certified'}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

