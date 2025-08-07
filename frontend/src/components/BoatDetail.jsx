import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/hooks/use-toast'
import { ArrowLeft, Upload, Download, TrendingUp, FileText } from 'lucide-react'

export default function BoatDetail() {
  const { boatId } = useParams()
  const [boat, setBoat] = useState(null)
  const [loading, setLoading] = useState(true)
  
  const { getAuthHeaders, API_BASE } = useAuth()
  const { toast } = useToast()

  useEffect(() => {
    fetchBoat()
  }, [boatId])

  const fetchBoat = async () => {
    try {
      const response = await fetch(`${API_BASE}/boats/${boatId}`, {
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      })

      if (response.ok) {
        const data = await response.json()
        setBoat(data.boat)
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch boat details",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error while fetching boat details",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!boat) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Boat not found</h1>
          <Link to="/dashboard">
            <Button className="mt-4">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <Link to="/dashboard">
          <Button variant="outline" className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{boat.name}</h1>
            <p className="mt-2 text-gray-600">
              {boat.class_name || boat.boat_type}
              {boat.year_built && ` • Built ${boat.year_built}`}
            </p>
          </div>
          <Badge variant="secondary" className="text-lg px-3 py-1">
            {boat.boat_type}
          </Badge>
        </div>
      </div>

      {/* Boat Specifications */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Specifications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {boat.loa && (
              <div className="flex justify-between">
                <span className="text-gray-600">LOA:</span>
                <span className="font-medium">{boat.loa}m</span>
              </div>
            )}
            {boat.lwl && (
              <div className="flex justify-between">
                <span className="text-gray-600">LWL:</span>
                <span className="font-medium">{boat.lwl}m</span>
              </div>
            )}
            {boat.beam && (
              <div className="flex justify-between">
                <span className="text-gray-600">Beam:</span>
                <span className="font-medium">{boat.beam}m</span>
              </div>
            )}
            {boat.draft && (
              <div className="flex justify-between">
                <span className="text-gray-600">Draft:</span>
                <span className="font-medium">{boat.draft}m</span>
              </div>
            )}
            {boat.displacement && (
              <div className="flex justify-between">
                <span className="text-gray-600">Displacement:</span>
                <span className="font-medium">{boat.displacement}kg</span>
              </div>
            )}
            {boat.sail_area && (
              <div className="flex justify-between">
                <span className="text-gray-600">Sail Area:</span>
                <span className="font-medium">{boat.sail_area}m²</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {boat.keel_type && (
              <div className="flex justify-between">
                <span className="text-gray-600">Keel:</span>
                <span className="font-medium">{boat.keel_type}</span>
              </div>
            )}
            {boat.rig_type && (
              <div className="flex justify-between">
                <span className="text-gray-600">Rig:</span>
                <span className="font-medium">{boat.rig_type}</span>
              </div>
            )}
            {boat.hull_material && (
              <div className="flex justify-between">
                <span className="text-gray-600">Hull:</span>
                <span className="font-medium">{boat.hull_material}</span>
              </div>
            )}
            {boat.crew_size && (
              <div className="flex justify-between">
                <span className="text-gray-600">Crew Size:</span>
                <span className="font-medium">{boat.crew_size}</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Racing Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {boat.rating_system && (
              <div className="flex justify-between">
                <span className="text-gray-600">Rating System:</span>
                <span className="font-medium">{boat.rating_system}</span>
              </div>
            )}
            {boat.rating_value && (
              <div className="flex justify-between">
                <span className="text-gray-600">Rating:</span>
                <span className="font-medium">{boat.rating_value}</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Data Management */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              Log Files
            </CardTitle>
            <CardDescription>
              Upload Expedition log files to build polar models
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                {boat.log_file_count || 0} files uploaded
              </p>
              <Button>
                <Upload className="mr-2 h-4 w-4" />
                Upload Log Files
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="mr-2 h-5 w-5" />
              Polar Models
            </CardTitle>
            <CardDescription>
              Generated performance polars from your sailing data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                {boat.polar_count || 0} polars generated
              </p>
              <div className="space-y-2">
                <Button className="w-full">
                  <TrendingUp className="mr-2 h-4 w-4" />
                  Generate Polar
                </Button>
                <Button variant="outline" className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Latest
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Notes */}
      {boat.notes && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Notes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 whitespace-pre-wrap">{boat.notes}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

