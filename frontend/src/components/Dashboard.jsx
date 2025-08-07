import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/hooks/use-toast'
import CreateBoatDialog from '@/components/CreateBoatDialog'
import { Plus, Anchor, FileText, TrendingUp, Calendar } from 'lucide-react'

export default function Dashboard() {
  const [boats, setBoats] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  
  const { user, getAuthHeaders, API_BASE } = useAuth()
  const { toast } = useToast()

  useEffect(() => {
    fetchBoats()
  }, [])

  const fetchBoats = async () => {
    try {
      const response = await fetch(`${API_BASE}/boats`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      })

      if (response.ok) {
        const data = await response.json()
        setBoats(data.boats)
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch boats",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error while fetching boats",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleBoatCreated = (newBoat) => {
    setBoats([...boats, newBoat])
    setShowCreateDialog(false)
    toast({
      title: "Success",
      description: `Boat "${newBoat.name}" created successfully`
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name}
        </h1>
        <p className="mt-2 text-gray-600">
          Manage your boats and build performance polars from sailing data
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Boats</CardTitle>
            <Anchor className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{boats.length}</div>
            <p className="text-xs text-muted-foreground">
              Active boat profiles
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Log Files</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {boats.reduce((sum, boat) => sum + (boat.log_file_count || 0), 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Uploaded sailing sessions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Polars Generated</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {boats.reduce((sum, boat) => sum + (boat.polar_count || 0), 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Performance models created
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Boats Section */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Your Boats</h2>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Boat
        </Button>
      </div>

      {boats.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <Anchor className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No boats yet
            </h3>
            <p className="text-gray-600 mb-6">
              Get started by adding your first boat to begin building polar models
            </p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Your First Boat
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {boats.map((boat) => (
            <Card key={boat.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{boat.name}</CardTitle>
                    <CardDescription>
                      {boat.class_name || boat.boat_type}
                      {boat.year_built && ` • ${boat.year_built}`}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary">
                    {boat.boat_type}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* Boat specs */}
                  {boat.loa && (
                    <div className="text-sm text-gray-600">
                      LOA: {boat.loa}m
                      {boat.beam && ` • Beam: ${boat.beam}m`}
                    </div>
                  )}
                  
                  {/* Data stats */}
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Log Files:</span>
                    <span className="font-medium">{boat.log_file_count || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Polars:</span>
                    <span className="font-medium">{boat.polar_count || 0}</span>
                  </div>
                  
                  {/* Last updated */}
                  {boat.updated_at && (
                    <div className="flex items-center text-xs text-gray-500">
                      <Calendar className="mr-1 h-3 w-3" />
                      Updated {new Date(boat.updated_at).toLocaleDateString()}
                    </div>
                  )}
                  
                  <div className="pt-2">
                    <Link to={`/boat/${boat.id}`}>
                      <Button className="w-full" variant="outline">
                        View Details
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Boat Dialog */}
      <CreateBoatDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onBoatCreated={handleBoatCreated}
      />
    </div>
  )
}

