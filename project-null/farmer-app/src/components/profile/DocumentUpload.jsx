import { useRef } from 'react';
import { useUploadDocument, useDeleteDocument, useFarmerDocuments } from '../../hooks/useFarmer';
import Card, { CardTitle } from '../common/Card';
import Button from '../common/Button';
import { DOC_TYPES } from '../../utils/constants';
import { Upload, CheckCircle2, Trash2, FileText, Loader2 } from 'lucide-react';
import { formatDate } from '../../utils/formatters';
import { useTranslation } from 'react-i18next';
import toast from 'react-hot-toast';

export default function DocumentUpload() {
  const { t } = useTranslation();
  const { data: documents = [], isLoading } = useFarmerDocuments();
  const uploadDoc = useUploadDocument();
  const deleteDoc = useDeleteDocument();
  const fileInputRefs = useRef({});

  const handleUpload = async (docType, file) => {
    if (!file) return;

    // Validate file
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      toast.error('Only PDF, JPG, and PNG files are allowed');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    uploadDoc.mutate(
      { file, docType },
      {
        onSuccess: () => toast.success(`${docType.replace(/_/g, ' ')} uploaded!`),
        onError: () => toast.error('Upload failed. Please try again.'),
      }
    );
  };

  const handleDelete = (docId, docType) => {
    deleteDoc.mutate(docId, {
      onSuccess: () => toast.success(`${docType.replace(/_/g, ' ')} removed`),
      onError: () => toast.error('Failed to delete'),
    });
  };

  const getDocForType = (type) => documents.find((d) => d.doc_type === type);

  return (
    <Card>
      <CardTitle className="mb-4">{t('profile.documents')}</CardTitle>

      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 text-primary-600 animate-spin" />
        </div>
      ) : (
        <div className="space-y-3">
          {DOC_TYPES.map((docType) => {
            const doc = getDocForType(docType.value);
            const isUploaded = !!doc;

            return (
              <div
                key={docType.value}
                className={`flex items-center justify-between p-3 rounded-xl border ${
                  isUploaded ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <FileText className={`w-5 h-5 flex-shrink-0 ${isUploaded ? 'text-green-600' : 'text-gray-400'}`} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900">{docType.label_en}</p>
                    <p className="text-xs text-gray-500">{docType.label_hi}</p>
                    {isUploaded && doc.uploaded_at && (
                      <p className="text-xs text-green-600">Uploaded {formatDate(doc.uploaded_at)}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isUploaded ? (
                    <>
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                      <button
                        onClick={() => handleDelete(doc.id, docType.value)}
                        className="p-1.5 rounded-lg hover:bg-red-100 transition-colors cursor-pointer"
                        disabled={deleteDoc.isPending}
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </button>
                    </>
                  ) : (
                    <>
                      <input
                        ref={(el) => (fileInputRefs.current[docType.value] = el)}
                        type="file"
                        accept=".pdf,.jpg,.jpeg,.png"
                        className="hidden"
                        onChange={(e) => handleUpload(docType.value, e.target.files[0])}
                      />
                      <Button
                        variant="secondary"
                        size="sm"
                        icon={Upload}
                        loading={uploadDoc.isPending}
                        onClick={() => fileInputRefs.current[docType.value]?.click()}
                      >
                        {t('profile.upload')}
                      </Button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
