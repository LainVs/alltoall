import React, { useState, useEffect, useMemo } from 'react';
import {
  Upload, FileText, CheckCircle, XCircle,
  Loader2, ArrowRight, X, Search, Settings2,
  ChevronRight, Download, Languages
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const TRANSLATIONS = {
  zh: {
    title: 'All to All',
    subtitle: '欢迎回来',
    dropFiles: '点击或拖拽文件到这里',
    browseFiles: '支持选择多个文件',
    addMore: '添加更多文件',
    searchPlaceholder: '搜索目标格式 (例如 docx, md, pdf...)',
    noCommonFormats: '选中的文件没有共同的支持格式',
    noMatches: '未找到匹配的格式',
    keepOriginalName: '保留原始文件名',
    advanced: '高级设置',
    convertTo: '转换为',
    converting: '正在转换...',
    success: '全部转换完成！文件已开始下载。',
    error: '转换失败，请检查文件后重试。',
    processing: '正在处理 {count} 个文件...',
    defaultTarget: '...',
  },
  en: {
    title: 'All to All',
    subtitle: 'Professional-grade file conversion suite.',
    dropFiles: 'Drop files here',
    browseFiles: 'or click to browse multiple files',
    addMore: 'Add more files',
    searchPlaceholder: 'Search target format (e.g. docx, md, pdf...)',
    noCommonFormats: 'No common formats found for selected files',
    noMatches: 'No matches found',
    keepOriginalName: 'Keep original filenames',
    advanced: 'Advanced',
    convertTo: 'Convert to',
    converting: 'Converting...',
    success: 'All conversions complete! Your files have been downloaded.',
    error: 'Conversion failed. Please check your files and try again.',
    processing: 'Converting {count} file(s)...',
    defaultTarget: '...',
  }
};

function App() {
  const [language, setLanguage] = useState('zh');
  const [files, setFiles] = useState([]);
  const [supportedFormats, setSupportedFormats] = useState({});
  const [targetFormat, setTargetFormat] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [keepName, setKeepName] = useState(true);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const t = (key, params = {}) => {
    let text = TRANSLATIONS[language][key] || key;
    Object.keys(params).forEach(p => {
      text = text.replace(`{${p}}`, params[p]);
    });
    return text;
  };

  // 获取支持的格式
  useEffect(() => {
    const fetchFormats = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/formats`);
        setSupportedFormats(response.data);
      } catch (error) {
        console.error('Failed to fetch formats:', error);
        // Optionally, you could set a status/message here for format fetching errors
      }
    };
    fetchFormats();
  }, []);

  const onFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    addFiles(selectedFiles);
  };

  const addFiles = (newFiles) => {
    setFiles(prev => {
      const combined = [...prev, ...newFiles];
      // 去重基于文件名
      return combined.filter((file, index, self) =>
        index === self.findIndex((f) => f.name === file.name)
      );
    });
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  };

  // 根据当前文件列表计算可用的目标格式
  const availableTargetFormats = useMemo(() => {
    if (files.length === 0) return [];

    // 获取所有文件的后缀
    const exts = files.map(f => `.${f.name.split('.').pop().toLowerCase()}`);

    // 找出所有文件共同支持的目标格式（交集）
    if (exts.length === 0) return [];

    let intersection = supportedFormats[exts[0]] || [];
    for (let i = 1; i < exts.length; i++) {
      const targets = supportedFormats[exts[i]] || [];
      intersection = intersection.filter(fmt => targets.includes(fmt));
    }

    return intersection.sort();
  }, [files, supportedFormats]);

  // 搜索过滤后的格式
  const filteredFormats = useMemo(() => {
    return availableTargetFormats.filter(fmt =>
      fmt.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [availableTargetFormats, searchQuery]);

  const handleConvert = async () => {
    if (files.length === 0 || !targetFormat) return;

    setIsUploading(true);
    setProgress(0);
    setStatus('uploading');
    setMessage(t('processing', { count: files.length }));

    const totalFiles = files.length;
    let successCount = 0;
    let simulatedInterval;

    try {
      // 对每个文件进行转换以展示真实进度
      for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // 每个文件的进度区间
        const startProgress = (i / totalFiles) * 100;
        const endProgress = ((i + 1) / totalFiles) * 100;

        // 清除上一个文件的模拟计时器
        if (simulatedInterval) clearInterval(simulatedInterval);

        // 开启模拟增长：在该文件的 0% 到 90% 区间内缓慢增长
        let currentSimulated = 0;
        simulatedInterval = setInterval(() => {
          currentSimulated += (100 - currentSimulated) * 0.05; // 渐近增长
          const simulatedValue = startProgress + (currentSimulated / 100) * (endProgress - startProgress) * 0.9;
          setProgress(Math.round(simulatedValue));
        }, 300);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_format', targetFormat);
        formData.append('keep_name', keepName.toString());

        const response = await axios.post(`${API_BASE_URL}/convert`, formData, {
          responseType: 'blob',
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;

        let outputName = '';
        const contentDisposition = response.headers['content-disposition'];
        if (contentDisposition) {
          const match = contentDisposition.match(/filename="(.+)"/);
          if (match) outputName = match[1];
        }

        if (!outputName) {
          outputName = file.name.replace(/\.[^/.]+$/, "") + targetFormat;
        }

        link.setAttribute('download', outputName);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        successCount++;
        // 文件处理完，立即跳到该文件的 100% 进度
        setProgress(Math.round(endProgress));
      }

      if (simulatedInterval) clearInterval(simulatedInterval);
      setStatus('success');
      setMessage(t('success'));
      setFiles([]);
    } catch (err) {
      if (simulatedInterval) clearInterval(simulatedInterval);
      console.error('Conversion error:', err);
      
      let errorDetail = '';
      if (err.response && err.response.data instanceof Blob) {
        // Since responseType is 'blob', we need to read it to get the JSON error
        const reader = new FileReader();
        reader.onload = () => {
          try {
            const errorJson = JSON.parse(reader.result);
            console.error('Backend error:', errorJson.error);
            setMessage(errorJson.error || t('error'));
          } catch (e) {
            setMessage(t('error'));
          }
        };
        reader.readAsText(err.response.data);
      } else {
        setMessage(t('error'));
      }
      
      setStatus('error');
    }
 finally {
      // 延迟关闭上传状态以展示 100% 进度
      setTimeout(() => {
        setIsUploading(false);
        setProgress(0);
      }, 600);
    }
  };

  return (
    <div className="app-container">
      {/* 语言切换器 */}
      <div className="language-selector">
        <div
          className={`lang-option ${language === 'zh' ? 'active' : ''}`}
          onClick={() => setLanguage('zh')}
        >
          中
        </div>
        <div className="lang-divider"></div>
        <div
          className={`lang-option ${language === 'en' ? 'active' : ''}`}
          onClick={() => setLanguage('en')}
        >
          EN
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="glass-card"
      >
        <div className="title-section">
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {t('title')}
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {t('subtitle')}
          </motion.p>
        </div>

        {/* 文件上传区 */}
        <div
          className={`drop-zone ${isDragging ? 'dragging' : ''} ${files.length > 0 ? 'compact' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
          style={files.length > 0 ? { padding: '2rem' } : {}}
        >
          <input
            id="file-input"
            type="file"
            multiple
            hidden
            onChange={onFileChange}
          />
          <div className="icon-wrapper">
            {status === 'uploading' ? (
              <Loader2 className="animate-spin" size={files.length > 0 ? 24 : 32} />
            ) : (
              <Upload size={files.length > 0 ? 24 : 32} />
            )}
          </div>
          {files.length === 0 ? (
            <div style={{ textAlign: 'center' }}>
              <p style={{ marginBottom: '4px', fontWeight: '600' }}>{t('dropFiles')}</p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{t('browseFiles')}</p>
            </div>
          ) : (
            <p style={{ fontWeight: '600', fontSize: '0.9rem' }}>{t('addMore')}</p>
          )}
        </div>

        {/* 文件列表 */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="file-list"
            >
              {files.map((file, idx) => (
                <motion.div
                  key={`${file.name}-${idx}`}
                  layout
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="file-item"
                >
                  <div className="file-info">
                    <FileText size={16} color="var(--accent-color)" />
                    <span className="file-name">{file.name}</span>
                  </div>
                  <button className="remove-file" onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}>
                    <X size={14} />
                  </button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* 格式选择面板 */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="format-selection-panel"
            >
              <div className="search-container">
                <Search className="search-icon" size={16} />
                <input
                  type="text"
                  placeholder={t('searchPlaceholder')}
                  className="search-input"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div className="format-grid">
                {filteredFormats.length > 0 ? (
                  filteredFormats.map(fmt => (
                    <motion.div
                      key={fmt}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={`format-tag ${targetFormat === fmt ? 'selected' : ''}`}
                      onClick={() => setTargetFormat(fmt)}
                    >
                      {fmt.replace('.', '').toUpperCase()}
                    </motion.div>
                  ))
                ) : (
                  <p style={{ gridColumn: '1/-1', textAlign: 'center', fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '1rem' }}>
                    {availableTargetFormats.length === 0 ? t('noCommonFormats') : t('noMatches')}
                  </p>
                )}
              </div>

              <div className="options-container">
                <div
                  className={`toggle-container ${keepName ? 'active' : ''}`}
                  onClick={() => setKeepName(!keepName)}
                >
                  <div className="toggle-switch"></div>
                  <span className="toggle-label">{t('keepOriginalName')}</span>
                </div>
                <div className="selection-divider" style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem' }}>
                  <Settings2 size={14} />
                  <span>{t('advanced')}</span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          className="button"
          disabled={files.length === 0 || !targetFormat || status === 'uploading'}
          onClick={handleConvert}
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
        >
          {status === 'uploading' ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              <span>{t('converting')}</span>
            </>
          ) : (
            <>
              <span>{t('convertTo')} {targetFormat ? targetFormat.replace('.', '').toUpperCase() : t('defaultTarget')}</span>
              <ChevronRight size={18} />
            </>
          )}
        </button>

        <AnimatePresence>
          {isUploading && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="progress-wrapper"
            >
              <div className="progress-info">
                <span>{t('converting')}</span>
                <span>{progress}%</span>
              </div>
              <div className="progress-track">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                  className="progress-fill"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {message && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`status-message ${status === 'success' ? 'status-success' : status === 'error' ? 'status-error' : ''}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                {status === 'success' && <Download size={18} />}
                {status === 'error' && <XCircle size={18} />}
                <span>{message}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default App;
