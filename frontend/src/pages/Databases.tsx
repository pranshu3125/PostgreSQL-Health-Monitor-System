import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { databasesApi } from '../services/api'
import { Plus, Trash2, TestTube } from 'lucide-react'

export default function Databases() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '', host: '', port: 5432, database: '', username: '', password: '', description: ''
  })

  const { data: databases, isLoading } = useQuery({
    queryKey: ['databases'],
    queryFn: databasesApi.getAll,
  })

  const createMutation = useMutation({
    mutationFn: databasesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['databases'] })
      setShowForm(false)
      setFormData({ name: '', host: '', port: 5432, database: '', username: '', password: '', description: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: databasesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['databases'] })
    },
  })

  const testMutation = useMutation({
    mutationFn: databasesApi.test,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Database Connections</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" /> Add Database
        </button>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <h2 className="text-lg font-semibold mb-4">New Database Connection</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
            <input
              placeholder="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="border p-2 rounded"
              required
            />
            <input
              placeholder="Host"
              value={formData.host}
              onChange={(e) => setFormData({ ...formData, host: e.target.value })}
              className="border p-2 rounded"
              required
            />
            <input
              type="number"
              placeholder="Port"
              value={formData.port}
              onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
              className="border p-2 rounded"
              required
            />
            <input
              placeholder="Database"
              value={formData.database}
              onChange={(e) => setFormData({ ...formData, database: e.target.value })}
              className="border p-2 rounded"
              required
            />
            <input
              placeholder="Username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="border p-2 rounded"
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="border p-2 rounded"
              required
            />
            <input
              placeholder="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="border p-2 rounded col-span-2"
            />
            <button type="submit" className="bg-blue-600 text-white py-2 rounded col-span-2 hover:bg-blue-700">
              Create Connection
            </button>
          </form>
        </div>
      )}

      <div className="grid gap-4">
        {databases?.map((db: any) => (
          <div key={db.id} className="bg-white p-4 rounded-lg shadow flex justify-between items-center">
            <div>
              <h3 className="font-semibold">{db.name}</h3>
              <p className="text-sm text-gray-500">{db.host}:{db.port}/{db.database}</p>
              <p className="text-sm text-gray-400">{db.description}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => testMutation.mutate(db)}
                className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                title="Test Connection"
              >
                <TestTube className="w-5 h-5" />
              </button>
              <button
                onClick={() => deleteMutation.mutate(db.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
